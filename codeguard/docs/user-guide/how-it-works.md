# How CodeGuard Works

This guide explains CodeGuard's plagiarism detection process in non-technical terms.

## Overview

CodeGuard analyzes Python code files to detect plagiarism using three different detection methods. Each method looks for different types of copying, and a voting system combines their results to make a final decision.

## Why Three Detectors?

Different plagiarism techniques require different detection methods:

**Token Detector** - Catches direct copying
- Compares code word-by-word
- Fast and simple
- Detects exact copies or near-exact copies
- Cannot detect plagiarism if variable names are changed

**AST Detector** - Catches structural copying
- Analyzes the structure and logic of code
- Ignores variable and function names
- Detects plagiarism even when names are changed
- Cannot detect plagiarism if the algorithm itself is changed

**Hash Detector** - Catches partial copying
- Creates fingerprints of small code segments
- Detects when pieces of code are copied and rearranged
- Good at finding scattered copying
- Less effective against heavily modified code

By using all three methods, CodeGuard can detect a wide range of plagiarism techniques.

## How Does CodeGuard Decide?

CodeGuard uses a weighted voting system:

1. **Each detector analyzes the code** and produces a similarity score (0-100%)

2. **Each detector votes** if its score exceeds its threshold:
   - Token votes if similarity >= 70%
   - AST votes if similarity >= 80%
   - Hash votes if similarity >= 60%

3. **Votes are weighted** based on detector reliability:
   - AST vote counts 2.0x (most reliable)
   - Hash vote counts 1.5x (moderately reliable)
   - Token vote counts 1.0x (least reliable)

4. **Total possible votes: 4.5** (sum of all weights)

5. **Plagiarism is flagged** when weighted votes >= 2.25 (50% of total)

### Example Scenarios

**Scenario 1: Exact Copy**
- Token: 95% -> Votes (1.0x)
- AST: 98% -> Votes (2.0x)
- Hash: 92% -> Votes (1.5x)
- **Total: 4.5/4.5 votes -> PLAGIARIZED**

**Scenario 2: Variable Renaming**
- Token: 35% -> No vote
- AST: 95% -> Votes (2.0x)
- Hash: 40% -> No vote
- **Total: 2.0/4.5 votes (44%) -> CLEAR**
- (AST alone is not enough)

**Scenario 3: Structural Copy with Renaming**
- Token: 65% -> No vote
- AST: 88% -> Votes (2.0x)
- Hash: 72% -> Votes (1.5x)
- **Total: 3.5/4.5 votes (78%) -> PLAGIARIZED**
- (AST + Hash together detect it)

## Confidence Levels

In addition to plagiarism detection, CodeGuard provides a confidence score:

```
Confidence = (30% × Token) + (40% × AST) + (30% × Hash)
```

This represents overall similarity regardless of the plagiarism decision.

**Very High (90-100%)**: Near-identical code
**High (75-89%)**: Significant similarity
**Medium (50-74%)**: Moderate similarity
**Low (25-49%)**: Minor similarity
**Very Low (0-24%)**: Little to no similarity

### Confidence vs. Plagiarism Decision

- **High confidence + Plagiarized**: Strong evidence of copying
- **Medium confidence + Plagiarized**: Moderate evidence, worth reviewing
- **Low confidence + Clear**: Likely independent work
- **High confidence + Clear**: Similar but not enough votes (e.g., only Token matched)

## Adjustable Settings

Instructors can adjust detection sensitivity:

**Thresholds** - When each detector votes
- Lower threshold = more sensitive = more detections
- Higher threshold = less sensitive = fewer detections

**Weights** - How much each vote counts
- Higher weight = more influence on decision
- Default: AST (2.0x), Hash (1.5x), Token (1.0x)

**Decision Threshold** - Votes needed for plagiarism
- Lower threshold = easier to flag plagiarism
- Higher threshold = stricter plagiarism criteria
- Default: 50% of total possible votes

## Detector Agreement

CodeGuard also shows how well the detectors agree:

- **Strong Agreement**: All three give similar scores
- **Moderate Agreement**: Scores are reasonably close
- **Weak Agreement**: Significant differences between scores
- **Poor Agreement**: Detectors strongly disagree

High agreement increases confidence in the result.

## Summary

CodeGuard combines three complementary detection methods through weighted voting:
1. Each detector analyzes code independently
2. Detectors vote if their scores exceed thresholds
3. Votes are weighted by reliability
4. Plagiarism flagged when weighted votes >= 50%
5. Confidence score provides additional context

This multi-method approach makes CodeGuard robust against various plagiarism techniques while minimizing false positives.
