"""
grant_review.py
Side-by-side two-agent interface for collaborative grant proposal review.
Supports vulnerability analysis and reflection between agents.

Based on the "Flaws of Others" methodology for grant review consensus.

By Juan B. Gutiérrez, Professor of Mathematics 
University of Texas at San Antonio.

License: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)
"""

import os
import sys
import json
import base64
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QTextEdit, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QFileDialog, QMessageBox, QSplitter,
    QGroupBox, QScrollArea
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont

from cls_foo import MultiAgentOrchestrator
from cls_openai import OpenAIAgent
from cls_anthropic import AnthropicAgent


class BroadcastTextEdit(QTextEdit):
    """Custom QTextEdit for broadcast messages"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_widget = parent
        self.setMaximumHeight(100)
        self.setPlaceholderText("Type your question/message to broadcast to both agents (Shift+Enter for new line, Enter to send)")
        
    def keyPressEvent(self, event):
        """Handle Enter key for broadcasting"""
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if event.modifiers() & Qt.ShiftModifier:
                super().keyPressEvent(event)
            else:
                text = self.toPlainText().strip()
                if text and self.parent_widget:
                    self.parent_widget.broadcast_to_agents(text)
                    self.clear()
                return
        super().keyPressEvent(event)


class AgentTextEdit(QTextEdit):
    """Custom QTextEdit for individual agent input"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.agent_panel = parent
        self.setMaximumHeight(80)
        self.setPlaceholderText("Type message for this agent (Shift+Enter for new line, Enter to send)")
        
    def keyPressEvent(self, event):
        """Handle Enter key for individual messages"""
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if event.modifiers() & Qt.ShiftModifier:
                super().keyPressEvent(event)
            else:
                text = self.toPlainText().strip()
                if text and self.agent_panel:
                    self.agent_panel.send_individual_message(text)
                    self.clear()
                return
        super().keyPressEvent(event)


class AgentWorker(QThread):
    """Worker thread for agent message processing using orchestrator"""
    result_ready = pyqtSignal(str)
    
    def __init__(self, orchestrator, agent_name, message):
        super().__init__()
        self.orchestrator = orchestrator
        self.agent_name = agent_name
        self.message = message
    
    def run(self):
        try:
            # Use orchestrator's send_message_to_agent which handles history
            response = self.orchestrator.send_message_to_agent(self.agent_name, self.message)
            self.result_ready.emit(response)
        except Exception as e:
            self.result_ready.emit(f"Error: {e}")


class BroadcastWorker(QThread):
    """Worker thread for broadcast messages using orchestrator"""
    results_ready = pyqtSignal(dict)
    
    def __init__(self, orchestrator, message):
        super().__init__()
        self.orchestrator = orchestrator
        self.message = message
    
    def run(self):
        try:
            # Use orchestrator's broadcast_message which handles history
            responses = self.orchestrator.broadcast_message(self.message)
            self.results_ready.emit(responses)
        except Exception as e:
            self.results_ready.emit({"Error": str(e)})


class VulnerabilityWorker(QThread):
    """Worker thread for vulnerability analysis using orchestrator"""
    result_ready = pyqtSignal(str, str)  # (request, response)
    
    def __init__(self, orchestrator, source_agent_name, target_agent_name):
        super().__init__()
        self.orchestrator = orchestrator
        self.source_agent_name = source_agent_name
        self.target_agent_name = target_agent_name
    
    def run(self):
        try:
            source_agent = self.orchestrator.get_agent_by_name(self.source_agent_name)
            if not source_agent or not source_agent.latest_response:
                self.result_ready.emit("", "No response available from the other agent to analyze")
                return
            
            # Create vulnerability analysis prompt
            request_message = (
                f"The other agent ({self.source_agent_name}) provided the following response. "
                f"Your task is to critically analyze this response and identify any flaws, "
                f"weaknesses, unsupported claims, logical inconsistencies, or areas that need improvement:\n\n"
                f"{source_agent.latest_response}"
            )
            
            # Use orchestrator to send message (which handles history)
            response = self.orchestrator.send_message_to_agent(self.target_agent_name, request_message)
            self.result_ready.emit(request_message, response)
            
        except Exception as e:
            self.result_ready.emit("", f"Error: {e}")


class ReflectionWorker(QThread):
    """Worker thread for reflection analysis using orchestrator"""
    result_ready = pyqtSignal(str, str)  # (request, response)
    
    def __init__(self, orchestrator, source_agent_name, target_agent_name):
        super().__init__()
        self.orchestrator = orchestrator
        self.source_agent_name = source_agent_name  # Agent providing critique
        self.target_agent_name = target_agent_name  # Agent reflecting on its own work
    
    def run(self):
        try:
            source_agent = self.orchestrator.get_agent_by_name(self.source_agent_name)
            if not source_agent or not source_agent.latest_response:
                self.result_ready.emit("", "No critique available from the other agent")
                return
            
            # Create reflection prompt
            request_message = (
                f"The other agent ({self.source_agent_name}) has provided the following observations "
                f"and critique of your previous response. Please reflect on this feedback and regenerate "
                f"your response, addressing the valid concerns while explaining why you might disagree "
                f"with any points you find incorrect:\n\n"
                f"{source_agent.latest_response}"
            )
            
            # Use orchestrator to send message (which handles history)
            response = self.orchestrator.send_message_to_agent(self.target_agent_name, request_message)
            self.result_ready.emit(request_message, response)
            
        except Exception as e:
            self.result_ready.emit("", f"Error: {e}")


class PDFWorker(QThread):
    """Worker thread for PDF processing"""
    result_ready = pyqtSignal(str)
    
    def __init__(self, pdf_path, agent):
        super().__init__()
        self.pdf_path = pdf_path
        self.agent = agent
    
    def run(self):
        try:
            # Check if PyPDF2 is available
            try:
                import PyPDF2
            except ImportError:
                self.result_ready.emit(
                    "Error: PyPDF2 not installed. Install with: pip install PyPDF2"
                )
                return
            
            # Check if file exists
            if not os.path.exists(self.pdf_path):
                self.result_ready.emit(f"Error: File not found: {self.pdf_path}")
                return
            
            # Try to extract text from PDF
            text_content = []
            try:
                with open(self.pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    
                    # Check if PDF is encrypted
                    if pdf_reader.is_encrypted:
                        self.result_ready.emit("Error: PDF is encrypted. Please provide an unencrypted version.")
                        return
                    
                    for page_num, page in enumerate(pdf_reader.pages):
                        page_text = page.extract_text()
                        if page_text and page_text.strip():
                            text_content.append(f"--- Page {page_num + 1} ---\n{page_text}")
            
            except Exception as e:
                self.result_ready.emit(f"Error reading PDF: {str(e)}")
                return
            
            if text_content:
                full_text = "\n\n".join(text_content)
                # Limit text length to avoid overwhelming the API
                if len(full_text) > 50000:
                    full_text = full_text[:50000] + "\n\n[... Document truncated due to length ...]"
                self.result_ready.emit(f"Successfully extracted text from PDF:\n\n{full_text}")
            else:
                # If no text extracted, likely a scanned PDF
                self.result_ready.emit(
                    "PDF appears to be scanned (no extractable text found). "
                    "OCR processing would be needed for this document. "
                    "Please provide a text-based PDF or use an OCR tool first."
                )
                
        except Exception as e:
            self.result_ready.emit(f"Error processing PDF: {str(e)}")


class AgentPanel(QGroupBox):
    """Panel for a single agent with controls"""
    
    def __init__(self, orchestrator, agent=None, other_panel=None, parent=None):
        super().__init__(parent)
        self.orchestrator = orchestrator
        self.agent = agent
        self.other_panel = other_panel
        self.parent_window = parent
        self.worker = None
        self.vulnerability_worker = None
        self.reflection_worker = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the agent panel UI"""
        layout = QVBoxLayout()
        
        # Agent selector (if multiple agents available)
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("Agent:"))
        self.agent_selector = QComboBox()
        self.populate_agent_selector()
        self.agent_selector.currentIndexChanged.connect(self.on_agent_changed)
        selector_layout.addWidget(self.agent_selector)
        selector_layout.addStretch()
        layout.addLayout(selector_layout)
        
        # Output area
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setMinimumHeight(300)
        layout.addWidget(QLabel("Agent Output:"))
        layout.addWidget(self.output_area)
        
        # Individual input area
        layout.addWidget(QLabel("Individual Message:"))
        self.input_area = AgentTextEdit(self)
        layout.addWidget(self.input_area)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.vulnerability_btn = QPushButton("🔍 Vulnerability")
        self.vulnerability_btn.setToolTip("Ask the other agent to find flaws in this agent's response")
        self.vulnerability_btn.clicked.connect(self.on_vulnerability_clicked)
        button_layout.addWidget(self.vulnerability_btn)
        
        self.reflection_btn = QPushButton("🔄 Reflection")
        self.reflection_btn.setToolTip("Use the other agent's critique to improve this agent's response")
        self.reflection_btn.clicked.connect(self.on_reflection_clicked)
        button_layout.addWidget(self.reflection_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.update_title()
    
    def populate_agent_selector(self):
        """Populate the agent selector dropdown"""
        self.agent_selector.clear()
        
        # Get all active agents
        agents = [a for a in self.orchestrator.agents if a.active]
        
        for agent in agents:
            self.agent_selector.addItem(agent.name, agent)
        
        # Set current agent if provided
        if self.agent:
            for i in range(self.agent_selector.count()):
                if self.agent_selector.itemData(i) == self.agent:
                    self.agent_selector.setCurrentIndex(i)
                    break
    
    def on_agent_changed(self, index):
        """Handle agent selection change"""
        self.agent = self.agent_selector.itemData(index)
        self.update_title()
        self.output_area.clear()
    
    def update_title(self):
        """Update panel title"""
        if self.agent:
            self.setTitle(f"Agent: {self.agent.name}")
        else:
            self.setTitle("Agent Panel")
    
    def set_other_panel(self, other_panel):
        """Set reference to the other agent panel"""
        self.other_panel = other_panel
    
    def send_individual_message(self, message):
        """Send message to this agent only"""
        if not self.agent:
            self.output_area.append("\n❌ No agent selected\n")
            return
        
        self.output_area.append(f"\n{'='*60}")
        self.output_area.append(f"📤 You → {self.agent.name}:")
        self.output_area.append(message)
        self.output_area.append(f"{'='*60}\n")
        
        self.input_area.setEnabled(False)
        self.vulnerability_btn.setEnabled(False)
        self.reflection_btn.setEnabled(False)
        
        # Use orchestrator worker
        self.worker = AgentWorker(self.orchestrator, self.agent.name, message)
        self.worker.result_ready.connect(self.on_response_ready)
        self.worker.start()
    
    def receive_broadcast_response(self, agent_name, response):
        """Receive broadcast response for this agent"""
        if self.agent and self.agent.name == agent_name:
            self.output_area.append(f"💬 {agent_name} responds:")
            self.output_area.append(response)
            self.output_area.append("\n")
            
            self.input_area.setEnabled(True)
            self.vulnerability_btn.setEnabled(True)
            self.reflection_btn.setEnabled(True)
    
    def on_response_ready(self, response):
        """Handle agent response"""
        self.output_area.append(f"💬 {self.agent.name} responds:")
        self.output_area.append(response)
        self.output_area.append("\n")
        
        self.input_area.setEnabled(True)
        self.vulnerability_btn.setEnabled(True)
        self.reflection_btn.setEnabled(True)
    
    def on_vulnerability_clicked(self):
        """Handle vulnerability button click"""
        if not self.agent or not self.other_panel or not self.other_panel.agent:
            QMessageBox.warning(self, "Error", "Both agents must be selected")
            return
        
        if not self.agent.latest_response:
            QMessageBox.warning(self, "Error", f"No response available from {self.agent.name} to analyze")
            return
        
        # Disable buttons during processing
        self.vulnerability_btn.setEnabled(False)
        self.reflection_btn.setEnabled(False)
        self.input_area.setEnabled(False)
        
        # Show in other panel that vulnerability analysis is starting
        self.other_panel.output_area.append(f"\n{'='*60}")
        self.other_panel.output_area.append(f"🔍 Vulnerability Analysis Request:")
        self.other_panel.output_area.append(f"Analyzing {self.agent.name}'s response for flaws...")
        self.other_panel.output_area.append(f"{'='*60}\n")
        
        # Start vulnerability analysis in the OTHER agent using orchestrator
        self.vulnerability_worker = VulnerabilityWorker(
            self.orchestrator, 
            self.agent.name, 
            self.other_panel.agent.name
        )
        self.vulnerability_worker.result_ready.connect(self.on_vulnerability_ready)
        self.vulnerability_worker.start()
    
    def on_vulnerability_ready(self, request, response):
        """Handle vulnerability analysis results"""
        if self.other_panel:
            self.other_panel.output_area.append(f"📋 Request sent to {self.other_panel.agent.name}:")
            self.other_panel.output_area.append(request[:200] + "..." if len(request) > 200 else request)
            self.other_panel.output_area.append(f"\n💬 {self.other_panel.agent.name}'s vulnerability analysis:")
            self.other_panel.output_area.append(response)
            self.other_panel.output_area.append("\n")
        
        # Re-enable buttons
        self.vulnerability_btn.setEnabled(True)
        self.reflection_btn.setEnabled(True)
        self.input_area.setEnabled(True)
    
    def on_reflection_clicked(self):
        """Handle reflection button click"""
        if not self.agent or not self.other_panel or not self.other_panel.agent:
            QMessageBox.warning(self, "Error", "Both agents must be selected")
            return
        
        if not self.other_panel.agent.latest_response:
            QMessageBox.warning(self, "Error", f"No critique available from {self.other_panel.agent.name}")
            return
        
        # Disable buttons during processing
        self.vulnerability_btn.setEnabled(False)
        self.reflection_btn.setEnabled(False)
        self.input_area.setEnabled(False)
        
        self.output_area.append(f"\n{'='*60}")
        self.output_area.append(f"🔄 Reflection Request:")
        self.output_area.append(f"Using {self.other_panel.agent.name}'s critique to improve response...")
        self.output_area.append(f"{'='*60}\n")
        
        # Start reflection analysis for THIS agent using OTHER agent's critique via orchestrator
        self.reflection_worker = ReflectionWorker(
            self.orchestrator,
            self.other_panel.agent.name,
            self.agent.name
        )
        self.reflection_worker.result_ready.connect(self.on_reflection_ready)
        self.reflection_worker.start()
    
    def on_reflection_ready(self, request, response):
        """Handle reflection results"""
        self.output_area.append(f"📋 Reflection prompt:")
        self.output_area.append(request[:200] + "..." if len(request) > 200 else request)
        self.output_area.append(f"\n💬 {self.agent.name}'s refined response:")
        self.output_area.append(response)
        self.output_area.append("\n")
        
        # Re-enable buttons
        self.vulnerability_btn.setEnabled(True)
        self.reflection_btn.setEnabled(True)
        self.input_area.setEnabled(True)


class GrantReviewGUI(QWidget):
    """Main window for grant review with two agents side-by-side"""
    
    def __init__(self, config_file="config.json"):
        super().__init__()
        self.config_file = config_file
        self.orchestrator = MultiAgentOrchestrator(config_file)
        
        # Get active agents
        active_agents = [a for a in self.orchestrator.agents if a.active]
        
        # Select first two agents by default
        self.agent1 = active_agents[0] if len(active_agents) > 0 else None
        self.agent2 = active_agents[1] if len(active_agents) > 1 else active_agents[0] if len(active_agents) > 0 else None

        # Store reference to PDF worker to prevent garbage collection
        self.pdf_worker = None
        self.broadcast_worker = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the main UI"""
        self.setWindowTitle("Grant Review - Collaborative Agent Analysis")
        self.setGeometry(100, 100, 1400, 800)
        
        main_layout = QVBoxLayout()
        
        # Title
        title = QLabel("Grant Review: Two-Agent Collaborative Analysis")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Instructions
        instructions = QLabel(
            "Broadcast messages to both agents below. Use Vulnerability to find flaws, "
            "and Reflection to improve responses based on critique."
        )
        instructions.setWordWrap(True)
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setStyleSheet("color: #666; padding: 10px;")
        main_layout.addWidget(instructions)
        
        # Broadcast area
        broadcast_group = QGroupBox("Broadcast Message to Both Agents")
        broadcast_layout = QVBoxLayout()
        self.broadcast_input = BroadcastTextEdit(self)
        broadcast_layout.addWidget(self.broadcast_input)
        
        # PDF upload button
        pdf_button_layout = QHBoxLayout()
        self.upload_pdf_btn = QPushButton("📄 Upload PDF/Document")
        self.upload_pdf_btn.clicked.connect(self.upload_pdf)
        pdf_button_layout.addWidget(self.upload_pdf_btn)
        pdf_button_layout.addStretch()
        broadcast_layout.addLayout(pdf_button_layout)
        
        broadcast_group.setLayout(broadcast_layout)
        main_layout.addWidget(broadcast_group)
        
        # Splitter for two agent panels
        splitter = QSplitter(Qt.Horizontal)
        
        # Create agent panels
        self.panel1 = AgentPanel(self.orchestrator, self.agent1, None, self)
        self.panel2 = AgentPanel(self.orchestrator, self.agent2, None, self)
        
        # Set cross-references
        self.panel1.set_other_panel(self.panel2)
        self.panel2.set_other_panel(self.panel1)
        
        splitter.addWidget(self.panel1)
        splitter.addWidget(self.panel2)
        splitter.setSizes([700, 700])
        
        main_layout.addWidget(splitter, 1)
        
        # Control buttons
        control_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Save Conversation")
        save_btn.clicked.connect(self.save_conversation)
        control_layout.addWidget(save_btn)
        
        load_btn = QPushButton("📂 Load Conversation")
        load_btn.clicked.connect(self.load_conversation)
        control_layout.addWidget(load_btn)
        
        clear_btn = QPushButton("🗑️ Clear All")
        clear_btn.clicked.connect(self.clear_all)
        control_layout.addWidget(clear_btn)
        
        control_layout.addStretch()
        
        exit_btn = QPushButton("❌ Exit")
        exit_btn.clicked.connect(self.close)
        control_layout.addWidget(exit_btn)
        
        main_layout.addLayout(control_layout)
        
        self.setLayout(main_layout)
    
    def broadcast_to_agents(self, message):
        """Broadcast message to both agents using orchestrator"""
        # Display broadcast message in both panels
        self.panel1.output_area.append(f"\n{'='*60}")
        self.panel1.output_area.append(f"📢 Broadcast → {self.panel1.agent.name if self.panel1.agent else 'Agent'}:")
        self.panel1.output_area.append(message)
        self.panel1.output_area.append(f"{'='*60}\n")
        
        self.panel2.output_area.append(f"\n{'='*60}")
        self.panel2.output_area.append(f"📢 Broadcast → {self.panel2.agent.name if self.panel2.agent else 'Agent'}:")
        self.panel2.output_area.append(message)
        self.panel2.output_area.append(f"{'='*60}\n")
        
        # Disable inputs
        self.panel1.input_area.setEnabled(False)
        self.panel1.vulnerability_btn.setEnabled(False)
        self.panel1.reflection_btn.setEnabled(False)
        
        self.panel2.input_area.setEnabled(False)
        self.panel2.vulnerability_btn.setEnabled(False)
        self.panel2.reflection_btn.setEnabled(False)
        
        # Use orchestrator's broadcast_message
        self.broadcast_worker = BroadcastWorker(self.orchestrator, message)
        self.broadcast_worker.results_ready.connect(self.on_broadcast_responses)
        self.broadcast_worker.start()
    
    def on_broadcast_responses(self, responses):
        """Handle broadcast responses from orchestrator"""
        for agent_name, response in responses.items():
            # Send response to appropriate panel
            self.panel1.receive_broadcast_response(agent_name, response)
            self.panel2.receive_broadcast_response(agent_name, response)
    
    def upload_pdf(self):
        """Handle PDF upload"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select PDF or Document",
            "",
            "PDF Files (*.pdf);;All Files (*)"
        )
        
        if not file_path:
            return
        
        # Display in broadcast that file is being processed
        filename = os.path.basename(file_path)
        self.broadcast_input.setText(f"[Processing: {filename}]")
        
        # Disable upload button while processing
        self.upload_pdf_btn.setEnabled(False)
        
        # Process PDF - store reference to prevent garbage collection
        self.pdf_worker = PDFWorker(file_path, None)
        self.pdf_worker.result_ready.connect(self.on_pdf_processed)
        self.pdf_worker.finished.connect(self.on_pdf_worker_finished)
        self.pdf_worker.start()
        
    def on_pdf_worker_finished(self):
        """Clean up after PDF worker completes"""
        # Re-enable upload button
        self.upload_pdf_btn.setEnabled(True)
        
        # Clean up worker reference
        if self.pdf_worker:
            self.pdf_worker.deleteLater()
            self.pdf_worker = None    
            
    def on_pdf_processed(self, result):
        """Handle processed PDF content"""
        # Check if processing was successful
        if result.startswith("Error") or result.startswith("PDF appears to be scanned"):
            QMessageBox.warning(self, "PDF Processing", result)
            self.broadcast_input.clear()
            return
        
        # Create a message with the PDF content
        message = f"Please analyze the following document:\n\n{result}"
        
        # Broadcast to both agents
        self.broadcast_to_agents(message)
        
        # Clear the processing message
        self.broadcast_input.clear()
    
    def save_conversation(self):
        """Save conversation to file"""
        try:
            # Save each agent's conversation
            # The orchestrator has been updating history throughout
            for agent in self.orchestrator.agents:
                agent.save_conversation()
            
            QMessageBox.information(self, "Success", "Conversations saved successfully")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save conversations: {e}")
    
    def load_conversation(self):
        """Load conversation from file"""
        folder = QFileDialog.getExistingDirectory(self, "Select Folder with Agent Files")
        
        if not folder:
            return
        
        try:
            results = self.orchestrator.load_agent_files(folder)
            
            # Display results
            result_text = "\n".join([f"{name}: {result}" for name, result in results.items()])
            QMessageBox.information(self, "Load Results", result_text)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load conversations: {e}")
    
    def clear_all(self):
        """Clear all output areas"""
        reply = QMessageBox.question(
            self,
            "Clear All",
            "Are you sure you want to clear all output areas?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.panel1.output_area.clear()
            self.panel2.output_area.clear()
            self.broadcast_input.clear()
    
def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    
    # File selection dialog for configuration
    config_file = None
    
    # Check if config file provided via command line
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
        if not os.path.exists(config_file):
            QMessageBox.critical(None, "Error", f"Config file not found: {config_file}")
            sys.exit(1)
    else:
        # Show file selection dialog
        config_file, _ = QFileDialog.getOpenFileName(
            None,
            "Select Configuration File",
            "",
            "Config Files (config*.json);;JSON Files (*.json);;All Files (*)"
        )
        
        if not config_file:
            QMessageBox.information(None, "No Config Selected", "No configuration file selected. Exiting.")
            sys.exit(0)
    
    try:
        window = GrantReviewGUI(config_file)
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Failed to initialize application:\n{str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()