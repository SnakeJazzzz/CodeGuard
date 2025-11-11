# Technical Decisions Log

## Purpose
This document tracks all significant technical decisions, architecture changes, and development pivots made during the CodeGuard project development. It serves as a historical record of why certain choices were made, alternatives considered, and impacts on the project.

## Table of Contents
1. [Flask to Streamlit Migration - November 2024](#decision-001-flask-to-streamlit-migration)
2. [Future Decisions](#future-decisions)

---

## Decision 001: Flask to Streamlit Migration
**Date:** November 11, 2024
**Status:** ✅ Approved and Implemented
**Decision Makers:** Michael Andrew Devlyn Roach, Roberto Castro Soto

### Context
The original project design specified Flask web framework with separate HTML/CSS/JS frontend components (templates/, static/ directories). The project is an academic assignment (15-week semester) for Algorithm Design and Analysis course at Instituto Tecnológico y de Estudios Superiores de Monterrey.

**Initial Architecture:**
- Flask 3.0 web framework
- HTML templates with Jinja2
- CSS for styling (main.css, upload.css, results.css)
- JavaScript for interactivity (upload.js, results.js, progress.js)
- Separate src/web/ module for routes, forms, file handling

**Key Constraint:** Primary learning objective is algorithm implementation (Token, AST, Hash detectors + Voting System), not web development.

### Decision
Migrate from Flask to Streamlit for the web interface while maintaining all core algorithm implementations unchanged.

### Rationale

#### Advantages of Streamlit

1. **Development Speed (Critical for 15-week timeline)**
   - ~70% reduction in UI code (300 lines vs 1000+ lines)
   - Single Python file (app.py) vs multiple HTML/CSS/JS files
   - No context switching between languages
   - Faster iteration and debugging

2. **Learning Focus Alignment**
   - More time for core algorithms (project focus)
   - Reduced web development learning curve
   - Team expertise in Python, not web technologies
   - Better ROI for academic learning objectives

3. **Deployment Simplicity**
   - Free deployment via Streamlit Cloud (streamlit.io/cloud)
   - No server configuration required
   - One-click deployment from GitHub
   - Docker support maintained for local/custom deployments

4. **Built-in Features**
   - File upload/download handling
   - Progress indicators
   - Metrics and charts
   - Responsive layout (mobile-friendly)
   - Session state management
   - Configuration sliders/inputs

5. **Code Maintainability**
   - Easier to debug (single language)
   - Less moving parts
   - Better suited for academic project scope
   - Cleaner code review for professors

6. **Team Comfort Level**
   - Both team members proficient in Python
   - Limited web development experience
   - Reduced risk of UI bugs distracting from algorithm work

#### Disadvantages Considered

1. **Less Professional Appearance**
   - Streamlit has characteristic look/feel
   - Limited UI customization compared to custom HTML/CSS
   - **Mitigation:** Focus on functionality over aesthetics for academic project

2. **Not Learning Flask (Original Requirement)**
   - Flask experience not gained
   - Web development skills not practiced
   - **Mitigation:** Core algorithm skills are primary objective

3. **Framework Lock-in**
   - Harder to migrate away from Streamlit later
   - **Mitigation:** Modular architecture keeps detectors framework-independent

### Alternatives Considered

1. **Keep Flask**
   - **Pros:** Original plan, more professional, learns full-stack
   - **Cons:** Higher complexity, more time, risk to timeline
   - **Why Rejected:** Risk too high for academic project timeline

2. **No Web Interface (CLI only)**
   - **Pros:** Simplest, fastest to implement
   - **Cons:** Doesn't meet project requirements for user interface
   - **Why Rejected:** Requirements specify web interface

3. **Simple HTML + Python Server**
   - **Pros:** Lightweight, no framework overhead
   - **Cons:** Still requires HTML/CSS/JS knowledge, reinventing wheel
   - **Why Rejected:** More work than Streamlit with fewer features

4. **Gradio (Alternative to Streamlit)**
   - **Pros:** Similar to Streamlit, ML-focused
   - **Cons:** Less mature, smaller community, fewer features
   - **Why Rejected:** Streamlit more established and better documented

### Impact

#### What Stays the Same (95% of project - Core Academic Value)

✅ **All Detection Algorithms:**
- Token-based detector (lexical analysis)
- AST-based detector (structural comparison)
- Hash-based detector (Winnowing algorithm)

✅ **Voting System:**
- Weighted voting mechanism
- Confidence score calculation
- Threshold configuration

✅ **Database Layer:**
- SQLite for result storage
- Data persistence
- Query operations

✅ **Utilities:**
- File validation
- Logging
- Constants

✅ **Testing Requirements:**
- ≥80% code coverage target
- Unit tests for all detectors
- Integration tests for workflows

✅ **Documentation:**
- Algorithm documentation
- README files
- Code comments
- User guides

✅ **Core Project Objectives:**
- Plagiarism detection accuracy (≥85% precision, ≥80% recall)
- Multi-method approach
- Academic integrity tool

#### What Changes (5% of project - Implementation Details)

🔄 **UI Framework:**
- Flask → Streamlit
- File: src/web/* → app.py

🔄 **Project Structure:**
- Removed: templates/, static/, src/web/
- Added: app.py, .streamlit/config.toml

🔄 **Deployment:**
- Flask + Gunicorn → Streamlit server
- Port: 5000 → 8501
- Deployment option: Streamlit Cloud (free)

🔄 **Configuration:**
- Simplified: Single .streamlit/config.toml
- Removed: Flask-specific configs

🔄 **Dependencies:**
- Removed: Flask, Werkzeug, Flask-WTF
- Added: Streamlit, pandas (for data display)

### Implementation Plan

1. ✅ **Phase 1: Restructure Project**
   - Delete Flask-specific folders (templates/, static/, src/web/)
   - Create app.py with Streamlit interface
   - Update requirements.txt

2. ✅ **Phase 2: Create Docker Configuration**
   - Simplified Dockerfile for Streamlit
   - Updated docker-compose.yml
   - Added .dockerignore

3. ✅ **Phase 3: Update Documentation**
   - Rewrite main README.md
   - Update all module README files
   - Create technical decisions log

4. ⏳ **Phase 4: Implement Detectors** (Next)
   - Implement TokenDetector class
   - Implement ASTDetector class
   - Implement HashDetector class
   - Implement VotingSystem class

5. ⏳ **Phase 5: Integration**
   - Connect detectors to Streamlit UI
   - Test file upload and analysis workflow
   - Implement result visualization

6. ⏳ **Phase 6: Testing & Validation**
   - Unit tests for all components
   - Integration tests
   - Validation dataset testing
   - Achieve ≥80% coverage

7. ⏳ **Phase 7: Deployment**
   - Deploy to Streamlit Cloud
   - Test public accessibility
   - Create user documentation

### Success Metrics

**Technical Metrics:**
- ✅ Streamlit app runs without errors
- ⏳ All detectors integrated and functional
- ⏳ File upload/download works correctly
- ⏳ Results display accurately
- ⏳ Configuration sliders affect detection
- ⏳ ≥80% code coverage maintained

**Timeline Metrics:**
- ✅ Migration completed in 1 day
- ⏳ Working demo by Week 9
- ⏳ Full implementation by Week 13
- ⏳ Testing and documentation by Week 15

**Academic Metrics:**
- ⏳ Algorithm accuracy: ≥85% precision, ≥80% recall
- ⏳ Positive professor feedback on implementation
- ⏳ Project demonstrates algorithm design skills
- ⏳ Successful project defense

### Risk Mitigation

**Risk: Streamlit limitations discovered mid-project**
- Mitigation: Modular architecture allows Flask re-migration if needed
- Impact: ~2 days to revert to Flask if necessary

**Risk: Poor performance with Streamlit**
- Mitigation: Docker deployment option maintained
- Mitigation: Algorithm optimization independent of UI

**Risk: Deployment issues with Streamlit Cloud**
- Mitigation: Docker compose fallback for local/custom hosting
- Mitigation: Clear documentation for both deployment methods

### References

- [Streamlit Documentation](https://docs.streamlit.io)
- [Streamlit Cloud](https://streamlit.io/cloud)
- [CodeGuard Project Vision Document](Docs/Project%20Vision%20Document.md)
- [CodeGuard SRS](Docs/Software%20Requirements%20Specification%20(SRS).md)
- [Streamlit vs Flask Discussion](https://discuss.streamlit.io/)

### Notes

- Decision made after completing planning phase (Weeks 1-3)
- No algorithm implementation affected by this change
- Total time saved: Estimated 20-30 hours of development time
- This allows more time for algorithm optimization and testing
- Professor approval pending but confident in rationale

### Lessons Learned

1. **Early Pivots are Cheaper:** Making this decision before implementation saved significant time
2. **Focus on Core Objectives:** Web framework is implementation detail, algorithms are core value
3. **Team Skills Matter:** Choosing tools team is comfortable with reduces risk
4. **Document Decisions:** This log helps justify choices to stakeholders

---

## Future Decisions

### Template for New Entries

## Decision XXX: [Decision Title]
**Date:** [YYYY-MM-DD]
**Status:** [🤔 Proposed / ✅ Approved / ❌ Rejected / 🔄 In Progress / ✔️ Completed]
**Decision Makers:** [Names]

### Context
[What situation led to this decision? What problem are we trying to solve?]

### Decision
[What was decided? Be specific and concrete.]

### Rationale
[Why was this decision made? List advantages and disadvantages.]

### Alternatives Considered
[What other options were evaluated? Why were they not chosen?]

### Impact
[How does this affect the project? Consider: code, timeline, architecture, team, users]

### Implementation Plan
[Concrete steps to implement this decision with timeline]

### Success Metrics
[How will we measure if this decision was correct?]

### References
[Links to relevant documents, discussions, research, etc.]

### Notes
[Any additional context, concerns, or information]

---

## Decision History Summary

| ID | Date | Decision | Status | Impact |
|----|------|----------|--------|--------|
| 001 | 2024-11-11 | Flask to Streamlit Migration | ✅ Approved | High - Changed UI framework |

---

## Decision Categories

### Architecture Decisions
- Decision 001: Flask to Streamlit Migration

### Algorithm Decisions
- (None yet - pending implementation)

### Testing Decisions
- (None yet)

### Deployment Decisions
- Decision 001: Streamlit Cloud deployment option

### Performance Decisions
- (None yet)

---

*Last Updated: November 11, 2024*
*Document Owner: Michael Roach & Roberto Castro*
*Review Schedule: Updated as decisions are made*
