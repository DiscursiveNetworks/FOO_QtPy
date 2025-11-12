# 🔬 Grant Review Instructions 

## Overview
Select one proposal from the  [Discord #wa25 channel](https://discord.com/channels/1431729549502316576/1431731077604573275)  and announce your selection to avoid overlap. This study implements a multi-agent artificial intelligence system for collaborative grant proposal review based on the "Flaws of Others" methodology, as described in our Methods.

## Step 1: Grant Proposal Selection and Preparation

### 1.1 Proposal Selection
Select proposals ensuring:
- Different NIH institutes representation
- Various funding mechanisms (F31, R21, R01)
- Complete proposals with standard NIH structure

### 1.2 Document Preparation - Relevance Screening
Remove non-relevant pages, retaining only core scientific content (7-15 pages):

**KEEP These Sections:**
- Specific Aims (typically page 1)
- Research Strategy:
  - Significance
  - Innovation
  - Approach

**REMOVE These Sections:**
- Administrative forms
- Appendices
- Biographical sketches/CVs
- Budget pages and justifications
- Facilities & Other Resources
- Equipment lists
- Bibliography/References Cited
- Letters of support
- Other support pages
- Personnel justification

### 1.3 Structure Verification
Verify each proposal contains standard NIH sections beginning with Specific Aims, in accordance with the specific funding mechanism requirements.

### 1.4 Optical Character Recognition (OCR)
The folder `utils` contains several programs to conduct OCR. Process all proposals using OCR software to ensure machine-readable text extraction:

```bash
# Option 1: Use grant_extractor.py for automatic extraction
python grant_extractor.py original_proposal.pdf extracted/

# Option 2: Use Adobe Acrobat Pro DC with these settings:
# - Language: English (US)
# - Output: Searchable Image
# - Downsample to: 300 dpi
# - Compression: JPEG
# - Quality: High

# Then use grant_ocr.py for OCR
python grant_ocr.py extracted_proposal.pdf output/
```

**Note**: Manual verification of OCR accuracy is required, checking for:
- Special characters and symbols
- Mathematical equations
- Figure legends and table contents

## Step 2: Multi-Agent System Configuration

### 2.1 Configuration File Setup
Create individual configuration files based on the standardized template:

```bash
cp config_Gutierrez_NIH.json config_[YourName]_[GrantType].json
```

The configuration must include:
- Agent model specifications (e.g., GPT-4, Claude-3-opus)
- Standardized review prompt emphasizing NIH review criteria
- Instructions for comprehensive strength AND weakness identification
- Blockchain integrity verification settings

### 2.2 Agent Architecture
The system employs two independent AI agents:
- **Agent 1**: Primary reviewer (GPT-4 or Claude 3)
- **Agent 2**: Critical analyst (complementary AI model)

### 2.3 Review Prompt Requirements
Ensure the prompt explicitly requires identification of weaknesses for EACH criterion:

```
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

## Step 3: Review Process Implementation

### 3.1 System Initialization
```bash
python grant_review.py config_[YourName]_[GrantType].json
```

### 3.2 Document Upload
Upload the sanitized, OCR-processed PDF (7-15 pages of research content only).

### 3.3 Initial Review Phase
Agent 1 conducts comprehensive review. Ensure the agent provides:
- Detailed strengths for each NIH criterion
- Specific weaknesses and limitations (REQUIRED)
- Constructive recommendations for improvement

### 3.4 Iterative Refinement
Refine agent responses through:

1. **Response Enhancement**: Request expansion of abbreviated responses
   - "Please expand your analysis of [specific section]"
   - "Provide more detailed examples and specific citations"

2. **Detail Elaboration**: Query until full responses achieved
   - "Replace general statements with specific examples from the proposal"

3. **Weakness Identification**: Ensure balanced critique
   - "Your review lacks weaknesses for [criterion]. Please identify specific limitations"

## Step 4: Vulnerability Analysis Phase

### 4.1 Activate Vulnerability Analysis
Click "Vulnerability" button to prompt Agent 2 to analyze Agent 1's review for:
- Logical inconsistencies or contradictions
- Unsupported or exaggerated claims
- Overlooked critical weaknesses
- Potential reviewer bias
- Gaps in the analysis

### 4.2 Refine Vulnerability Analysis
Iterate until the critique includes:
- Specific, actionable criticisms
- Evidence-based challenges
- Constructive feedback
- Concrete examples from the original review

## Step 5: Reflection and Consensus Phase

### 5.1 Activate Reflection
Click "Reflection" button (NOT "Judgement" - this was corrected in the implementation) for the primary agent.

### 5.2 Response Integration
Agent 1 synthesizes the critique by:
- Accepting and incorporating valid criticisms
- Defending original assessments with additional evidence
- Modifying conclusions based on new perspectives
- Producing an updated, balanced final review

## Data Collection and Quality Assurance

### Automatic Logging
All interactions are logged with:
- Timestamp documentation
- Complete message history
- Blockchain integrity hashes
- JSON-formatted storage

### Quality Checklist
Before completing, verify:
- [ ] Only 7-15 pages of research content included
- [ ] All non-research sections removed
- [ ] OCR text clean and accurate
- [ ] Configuration uses standardized prompt
- [ ] Each criterion has identified weaknesses
- [ ] Specific proposal examples cited
- [ ] Vulnerability analysis completed
- [ ] Reflection synthesis performed
- [ ] All conversations saved (click "Save Conversation")

## Expected Outputs

Your review process generates:
1. `[AgentName].json` - Complete interaction history with blockchain hashes
2. Final balanced review incorporating vulnerability analysis
3. Evidence of iterative refinement
4. Comprehensive coverage of all NIH criteria with strengths AND weaknesses

## Common Issues and Solutions

### Missing Weaknesses
**Issue**: Agent provides only positive feedback
**Solution**: Explicitly request: "You must identify at least one weakness for each criterion. Even excellent proposals have areas for improvement."

### Generic Feedback
**Issue**: Reviews lack specific examples
**Solution**: Request: "Cite specific page numbers, figures, or quotes from the proposal to support each point."

### Incomplete Sections
**Issue**: Some NIH criteria not addressed
**Solution**: List missing sections explicitly: "Please provide analysis for: [missing sections]"

### Technical Errors
- **OCR issues**: Re-process at 300 dpi minimum
- **Configuration errors**: Verify JSON syntax
- **Save failures**: Check write permissions in output directory

## Alignment with Study Methodology

This process implements the methodology described in our manuscript:
- Standardized document preparation (7-15 pages)
- Dual-agent architecture for collaborative review
- Blockchain integrity for audit trails
- Iterative refinement process
- Vulnerability analysis ("Flaws of Others")
- Reflection-based consensus building

## Final Notes

1. **Weaknesses are mandatory**: NIH reviews always identify areas for improvement
2. **Balance is key**: Target 1:1 to 2:1 ratio of strengths to weaknesses
3. **Specificity matters**: General comments without examples are insufficient
4. **Save frequently**: Use "Save Conversation" button after major steps
5. **Document everything**: The JSON logs serve as your audit trail

---

**Remember**: This methodology enables systematic, reproducible evaluation of grant proposals while maintaining the rigor expected in actual NIH study sections.


# Grant Review Workflow - Methods-Aligned Visual Guide

## Complete Workflow 

```
┌─────────────────────────────────────────────────────────┐
│                  GRANT PROPOSAL SELECTION               │
│  • F31, R21, or R01 from different NIH institutes       │
│  • Complete proposals with standard structure           │
│  • Announce selection in #wa25 to prevent overlap       │
└───────────────────────┬─────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│                  DOCUMENT PREPARATION                   │
├─────────────────────────────────────────────────────────┤
│  1. Relevance Screening:                                │
│     REMOVE: • Administrative forms                      │
│             • Biographical sketches                     │
│             • Budget pages                              │
│             • Facilities & resources                    │
│             • References/Bibliography                   │
│     KEEP:   • Specific Aims                             │
│             • Research Strategy (Sig/Innov/Approach)    │
│                                                         │
│  2. Structure Verification:                             │
│     • Must begin with Specific Aims                     │
│     • 7-15 pages total                                  │
│                                                         │
│  3. OCR Processing:                                     │
│     • Adobe Acrobat Pro DC                              │
│     • Settings: 300 dpi, JPEG, High quality             │
│     • Manual verification required                      │
└───────────────────────┬─────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│              MULTI-AGENT SYSTEM CONFIGURATION           │
├─────────────────────────────────────────────────────────┤
│  • Copy config_Gutierrez_NIH.json template              │
│  • Agent 1: Primary reviewer (GPT-4/Claude 3)           │
│  • Agent 2: Critical analyst (complementary model)      │
│  • Prompt MUST require weaknesses for each criterion    │
│  • Blockchain integrity verification enabled            │
└───────────────────────┬─────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│                   INITIAL REVIEW PHASE                  │
├─────────────────────────────────────────────────────────┤
│  1. Launch: python grant_review.py config.json          │
│  2. Upload sanitized PDF (7-15 pages)                   │
│  3. Agent 1 provides:                                   │
│     • Detailed strengths per criterion                  │
│     • Specific weaknesses (REQUIRED)                    │
│     • Constructive recommendations                      │
└───────────────────────┬─────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│                  ITERATIVE REFINEMENT                   │
├─────────────────────────────────────────────────────────┤
│  Repeat until satisfactory:                             │
│  • "Expand analysis of [section]"                       │
│  • "Provide specific examples from proposal"            │
│  • "Identify weaknesses for [criterion]"                │
│  • "Balance positive and negative assessments"          │
└───────────────────────┬─────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│              VULNERABILITY ANALYSIS PHASE               │
├─────────────────────────────────────────────────────────┤
│  1. Click "Vulnerability" button                        │
│  2. Agent 2 analyzes Agent 1's review for:              │
│     • Logical inconsistencies                           │
│     • Unsupported claims                                │
│     • Overlooked weaknesses                             │
│     • Reviewer bias                                     │
│  3. Refine until specific, evidence-based               │
└───────────────────────┬─────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│            REFLECTION AND CONSENSUS PHASE               │
├─────────────────────────────────────────────────────────┤
│  1. Click "Reflection" button (NOT "Judgement")         │
│  2. Agent 1 synthesizes critique:                       │
│     • Incorporates valid criticisms                     │
│     • Defends justified assessments                     │
│     • Modifies based on new insights                    │
│  3. Produces final balanced review                      │
└───────────────────────┬─────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│              DATA COLLECTION AND STORAGE                │
├─────────────────────────────────────────────────────────┤
│  Automatic logging includes:                            │
│  • Timestamp documentation                              │
│  • Complete message history                             │
│  • Blockchain integrity hashes                          │
│  • JSON-formatted agent files                           │
│  • Click "Save Conversation" to persist                 │
└─────────────────────────────────────────────────────────┘
```

## Review Quality Metrics (Per Methods)

```
┌─────────────────────────────────────┐
│         ANALYSIS FRAMEWORK          │
├─────────────────────────────────────┤
│ 1. Comprehensiveness                │
│    □ All NIH criteria covered       │
│                                     │
│ 2. Balance                          │
│    □ Strengths identified           │
│    □ Weaknesses identified          │
│                                     │
│ 3. Specificity                      │
│    □ Concrete examples              │
│    □ Proposal citations             │
│                                     │
│ 4. Consistency                      │
│    □ Initial ↔ Final alignment      │
│                                     │
│ 5. Constructiveness                 │
│    □ Actionable improvements        │
└─────────────────────────────────────┘
```

## NIH Review Criteria Structure

```
Each criterion MUST include:
┌────────────────────────┐
│    OVERALL IMPACT      │
├────────────────────────┤
│ Strengths:    [Req'd]  │
│ Weaknesses:   [Req'd]  │
│ Recommendations:       │
└────────────────────────┘
        ↓ 
[Repeat for each:]
• Significance
• Investigator(s)  
• Innovation
• Approach
• Environment
```

## File Input/Output Flow

```
INPUT                          PROCESS                        OUTPUT
─────                          ───────                        ──────
Full_Grant.pdf       →    grant_extractor.py    →    Research_Only.pdf
(50+ pages)                                            (7-15 pages)
                                  ↓
                             grant_ocr.py         →    Research_OCR.txt
                                  ↓
                           grant_review.py        →    Agent1.json
                          + config.json                 Agent2.json
                                                       (with blockchain)
```

## Common Workflow Errors to Avoid

❌ Including budget/personnel pages → Only 7-15 research pages
❌ Missing weakness identification → Explicitly request weaknesses  
❌ Using "Judgement" button → Use "Reflection" button
❌ Generic feedback → Demand specific examples
❌ Skipping vulnerability phase → All phases required
❌ Not saving conversations → Data lost without JSON export

---

**This workflow exactly implements the methodology from the Methods section of the manuscript.**
