# Methods

## Study Design and Overview

We developed and evaluated a multi-agent artificial intelligence system for collaborative grant proposal review based on the "Flaws of Others" methodology. This study aimed to assess the effectiveness of AI-assisted peer review in identifying strengths and weaknesses in NIH grant proposals across different funding mechanisms (F31, R21, R01).

## Grant Proposal Selection and Preparation

### Proposal Selection
A diverse set of publicly available NIH grant proposals was selected for analysis, ensuring representation across multiple funding mechanisms. Each proposal was assigned to a single reviewer to prevent overlap. Selection criteria included:
- Proposals from different NIH institutes
- Various funding mechanisms (F31, R21, R01)
- Complete proposals with standard NIH structure (Specific Aims, Significance, Innovation, Approach)

### Document Preparation
Selected proposals underwent a standardized preparation process:
1. **Relevance Screening**: Non-relevant pages (administrative forms, appendices, biosketches) were removed, retaining only the core scientific content (typically 7-15 pages)
2. **Structure Verification**: Each proposal was verified to contain standard NIH sections beginning with Specific Aims, in accordance with the solicitation requirements for the respective funding mechanism
3. **Optical Character Recognition (OCR)**: All proposals were processed using OCR software (Adobe Acrobat Pro DC) to ensure machine-readable text extraction, with manual verification of OCR accuracy

## Multi-Agent System Configuration

### Agent Architecture
The review system employed two independent AI agents configured for collaborative analysis:
- **Agent 1**: Primary reviewer (GPT-4 or Claude 3)
- **Agent 2**: Critical analyst (complementary AI model)

### Configuration Development
Individual configuration files were created for each review session based on a standardized template (config_Gutierrez_NIH.json). Configuration parameters included:
- Agent model specifications
- Standardized review prompt emphasizing NIH review criteria
- Instructions for comprehensive strength and weakness identification
- Blockchain integrity verification settings for audit trail

### Review Prompt Standardization
All agents utilized identical base prompts incorporating NIH review criteria:
- Significance and potential impact
- Innovation and novelty
- Approach feasibility and rigor
- Investigator qualifications
- Research environment adequacy

Critically, prompts were modified to explicitly require identification of weaknesses for each evaluation criterion, addressing a gap in the original review guidelines.

## Review Process Implementation

### Initial Review Phase
1. **System Initialization**: The grant_review.py application was launched with the prepared configuration file
2. **Document Upload**: Sanitized, OCR-processed PDF proposals were uploaded through the graphical interface
3. **Primary Analysis**: Agent 1 conducted initial comprehensive review with explicit instructions to provide:
   - Detailed strengths for each NIH criterion
   - Specific weaknesses and limitations
   - Constructive recommendations for improvement

### Iterative Refinement
Reviewers engaged in iterative refinement of agent responses:
1. **Response Enhancement**: Individual agents were prompted to expand abbreviated responses, ensuring comprehensive coverage
2. **Detail Elaboration**: Agents were repeatedly queried until producing full, detailed responses for each review criterion
3. **Weakness Identification**: Special attention was given to ensuring balanced critique with both strengths and weaknesses documented

### Vulnerability Analysis Phase
Upon satisfactory completion of initial reviews:
1. **Cross-Agent Critique**: The "Vulnerability" function was activated, prompting Agent 2 to critically analyze Agent 1's review for:
   - Logical inconsistencies
   - Unsupported claims
   - Overlooked weaknesses
   - Biased assessments

2. **Critique Refinement**: The vulnerability analysis underwent iterative refinement until achieving:
   - Specific, actionable criticisms
   - Evidence-based challenges
   - Constructive feedback

### Reflection and Consensus Phase
Following vulnerability analysis:
1. **Reflection Process**: The "Reflection" function  was activated for the primary reviewing agent
2. **Response Integration**: Agent 1 synthesized the critique, either:
   - Accepting and incorporating valid criticisms
   - Defending original assessments with additional evidence
   - Modifying conclusions based on new perspectives

## Data Collection and Storage

### Conversation Logging
All agent interactions were automatically logged with:
- Timestamp documentation
- Complete message history
- Blockchain integrity hashes for audit trail
- JSON-formatted storage in agent-specific files

### Quality Assurance
- Manual verification of OCR accuracy
- Review completeness checks
- Interaction history validation
- Blockchain integrity verification

## Analysis Framework

Reviews were evaluated based on:
1. **Comprehensiveness**: Coverage of all NIH review criteria
2. **Balance**: Presence of both strengths and weaknesses
3. **Specificity**: Concrete examples and actionable feedback
4. **Consistency**: Agreement between initial and post-reflection assessments
5. **Constructiveness**: Quality of improvement suggestions

## Ethical Considerations

- All proposals analyzed were publicly available or used with permission
- No proprietary or confidential information was processed
- AI-generated reviews were clearly identified as such
- Human oversight was maintained throughout the process

## Software and Technical Specifications

- **Primary Application**: grant_review.py (v2.0)
- **AI Models**: GPT-4, Claude 3, and other large language models as specified in configuration files
- **OCR Software**: Adobe Acrobat Pro DC
- **Operating System**: Cross-platform (Windows, macOS, Linux)
- **Dependencies**: PyQt5, OpenAI API, Anthropic API, PyPDF2
- **Data Storage**: JSON format with blockchain integrity verification

This methodology enables systematic, reproducible evaluation of grant proposals using collaborative AI agents while maintaining rigorous documentation and quality control standards.

# Supplementary Methods

## Detailed Technical Specifications

### 1. Document Preprocessing Pipeline

#### 1.1 Proposal Structure Identification
- **Page Detection Algorithm**: Automated detection of standard NIH sections using keyword matching:
  - "Specific Aims" (typically page 1)
  - "Research Strategy" sections: Significance, Innovation, Approach
  - "Bibliography" and "Appendices" (marked for removal)

#### 1.2 OCR Processing Parameters
- **Software**: Adobe Acrobat Pro DC (version 2023.001.20174)
- **Settings**:
  - Language: English (US)
  - Output: Searchable Image
  - Downsample to: 300 dpi
  - Compression: JPEG
  - Quality: High
- **Quality Control**: Manual verification of:
  - Special characters and symbols
  - Mathematical equations
  - Figure legends and table contents
  - Formatting preservation

### 2. Configuration File Structure

```json
{
  "CONFIG": {
    "user": "Reviewer",
    "instructions": "You are an NIH study section reviewer...",
    "CWD": "/grant_reviews",
    "blockchain_salt": "[auto-generated]"
  },
  "MODELS": [
    {
      "model_code": "gpt-4",
      "agent_name": "Primary_Reviewer",
      "agent_directive": "Focus on comprehensive analysis with balanced critique",
      "active": true
    },
    {
      "model_code": "claude-3-opus",
      "agent_name": "Critical_Analyst",
      "agent_directive": "Identify flaws, gaps, and unsupported claims",
      "active": true
    }
  ]
}
```

### 3. Review Prompt Engineering

#### 3.1 Base Prompt Structure
```
You are an experienced NIH study section reviewer. Evaluate this proposal according to NIH review criteria.

For EACH section below, provide:
1. STRENGTHS: Specific positive aspects
2. WEAKNESSES: Specific limitations or concerns (REQUIRED)
3. RECOMMENDATIONS: Actionable improvements

Sections to evaluate:
- Overall Impact
- Significance
- Investigator(s)
- Innovation
- Approach
- Environment

Note: You MUST identify at least one weakness for each section.
```

#### 3.2 Iterative Refinement Prompts
- **Expansion prompt**: "Please expand your analysis of [specific section]. Provide more detailed examples and specific citations from the proposal."
- **Balance prompt**: "Your review appears overly [positive/negative]. Please provide a more balanced assessment with both strengths and weaknesses."
- **Specificity prompt**: "Replace general statements with specific examples from the proposal text."

### 4. Multi-Agent Interaction Protocol

#### 4.1 Message Flow
```
User → Agent1 (Initial Review)
     ↓
Agent1 Response → User (Refinement Loop)
     ↓
User → Agent2 (Vulnerability Request)
     ↓
Agent2 analyzes Agent1 → User
     ↓
User → Agent1 (Reflection Request)
     ↓
Agent1 synthesizes feedback → Final Review
```

#### 4.2 Vulnerability Analysis Instructions
```
Analyze the review provided by [Agent1] for:
1. Logical inconsistencies or contradictions
2. Unsupported or exaggerated claims
3. Overlooked critical weaknesses
4. Potential reviewer bias
5. Gaps in the analysis

Provide specific examples and suggest corrections.
```

#### 4.3 Reflection Protocol
```
Consider the critique provided by [Agent2]:
1. Identify valid criticisms to incorporate
2. Defend original assessments if well-supported
3. Modify conclusions based on new insights
4. Maintain professional tone throughout

Produce an updated, balanced review.
```

### 5. Data Storage and Integrity

#### 5.1 File Naming Convention
- Agent logs: `[AgentName].json`
- Blockchain verification: `[AgentName]_blockchain.json`
- Backup files: `[AgentName]_[timestamp].json.bak`

#### 5.2 JSON Structure
```json
{
  "history": [
    {
      "role": "user/assistant",
      "content": "message content",
      "timestamp": "ISO 8601 format",
      "blockchain": {
        "hash": "SHA256 hash",
        "previous_hash": "previous block hash",
        "index": 0
      }
    }
  ],
  "metadata": {
    "proposal_id": "identifier",
    "review_date": "date",
    "agent_version": "version"
  }
}
```

### 6. Quality Assurance Metrics

#### 6.1 Review Completeness Score
- Each section addressed: +1 point
- Strengths identified: +1 point
- Weaknesses identified: +2 points (required)
- Specific examples: +1 point
- Maximum score: 25 points per review

#### 6.2 Balance Assessment
- Strength-to-weakness ratio: Target 1:1 to 2:1
- Specificity index: Specific claims / Total claims
- Citation frequency: References to proposal / Total sentences

### 7. System Requirements

#### 7.1 Hardware
- Minimum RAM: 8 GB
- Recommended RAM: 16 GB
- Storage: 10 GB available space
- Network: Stable internet for API calls

#### 7.2 Software Dependencies
```
Python >= 3.8
PyQt5 >= 5.15.0
openai >= 1.0.0
anthropic >= 0.3.0
PyPDF2 >= 3.0.0
json (standard library)
datetime (standard library)
hashlib (standard library)
```

### 8. Workflow Diagram

```
┌─────────────────┐
│ Proposal PDF    │
└────────┬────────┘
         ↓
┌─────────────────┐
│ Remove Non-     │
│ Relevant Pages  │
└────────┬────────┘
         ↓
┌─────────────────┐
│ OCR Processing  │
└────────┬────────┘
         ↓
┌─────────────────┐
│ Configuration   │
│ File Creation   │
└────────┬────────┘
         ↓
┌─────────────────┐
│ grant_review.py │
│ Initialization  │
└────────┬────────┘
         ↓
┌─────────────────────────────┐
│ REVIEW CYCLE                │
│ ┌─────────────┐             │
│ │Initial Review│             │
│ └──────┬──────┘             │
│        ↓                     │
│ ┌─────────────┐             │
│ │  Refinement │ ←───┐       │
│ └──────┬──────┘     │       │
│        ↓            │       │
│ ┌─────────────┐     │       │
│ │Vulnerability│     │       │
│ │  Analysis   │     │       │
│ └──────┬──────┘     │       │
│        ↓            │       │
│ ┌─────────────┐     │       │
│ │ Reflection  ├─────┘       │
│ └──────┬──────┘             │
└────────┼────────────────────┘
         ↓
┌─────────────────┐
│ Final Review    │
│ & Data Storage  │
└─────────────────┘
```

### 9. Troubleshooting Guide

#### 9.1 Common Issues
- **OCR Errors**: Re-scan at higher DPI, check for skewed pages
- **API Timeouts**: Implement exponential backoff, check rate limits
- **Memory Issues**: Process proposals in chunks, clear agent history
- **Blockchain Errors**: Verify integrity, rebuild from last valid block

#### 9.2 Error Codes
- `E001`: OCR processing failed
- `E002`: API authentication error
- `E003`: Configuration file invalid
- `E004`: Blockchain integrity compromised
- `E005`: Agent response timeout

This supplementary material provides complete technical specifications for reproducing the multi-agent grant review methodology.