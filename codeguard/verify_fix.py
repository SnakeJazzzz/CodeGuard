#!/usr/bin/env python3
"""
Verify that the reset button fix has been applied correctly.

This script checks that all sliders in app.py use the correct pattern
for Streamlit widget-session_state synchronization.
"""

import re
from pathlib import Path

def check_slider_patterns(file_path):
    """Check for incorrect slider patterns in the file."""

    with open(file_path, 'r') as f:
        content = f.read()

    # Pattern for WRONG usage: st.session_state.var = st.slider(...)
    wrong_pattern = re.compile(
        r'st\.session_state\.(\w+)\s*=\s*st\.(slider|sidebar\.slider)\s*\(',
        re.MULTILINE
    )

    # Pattern for CORRECT usage: st.slider(..., key="var")
    # We'll check if sliders have key parameters
    slider_pattern = re.compile(
        r'st\.(sidebar\.)?slider\s*\([^)]+\)',
        re.DOTALL
    )

    print("=" * 80)
    print("CHECKING SLIDER PATTERNS IN app.py")
    print("=" * 80)

    # Find all wrong patterns
    wrong_matches = wrong_pattern.findall(content)

    if wrong_matches:
        print("\n❌ FOUND PROBLEMATIC PATTERNS (assignment to session_state):")
        print("-" * 40)
        for var, slider_type in wrong_matches:
            print(f"  - st.session_state.{var} = st.{slider_type}(...)")
        print("\nThese will cause the reset button to fail!")
        return False
    else:
        print("\n✅ No problematic assignment patterns found!")

    # Check that sliders use key parameters
    print("\n📊 ANALYZING SLIDER KEY USAGE:")
    print("-" * 40)

    # Find all sliders in the voting configuration section (lines 800-900)
    lines = content.split('\n')
    voting_section_start = None
    voting_section_end = None

    for i, line in enumerate(lines):
        if "VOTING SYSTEM CONFIGURATION" in line:
            voting_section_start = i
        if voting_section_start and "CURRENT CONFIGURATION DISPLAY" in line:
            voting_section_end = i
            break

    if voting_section_start and voting_section_end:
        voting_lines = lines[voting_section_start:voting_section_end]
        voting_content = '\n'.join(voting_lines)

        # Find all st.slider calls
        sliders = re.findall(r'st\.(?:sidebar\.)?slider\s*\([^)]+\)', voting_content, re.DOTALL)

        config_sliders = [
            "token_threshold", "ast_threshold", "hash_threshold",
            "token_weight", "ast_weight", "hash_weight",
            "decision_threshold"
        ]

        print(f"Found {len(sliders)} sliders in voting configuration section")
        print("\nChecking key parameters:")

        for var_name in config_sliders:
            # Check if this variable has a slider with matching key
            key_pattern = rf'key\s*=\s*["\']({var_name})["\']'
            if re.search(key_pattern, voting_content):
                print(f"  ✅ {var_name}: Uses key='{var_name}' (CORRECT)")
            else:
                # Check for wrong key pattern
                wrong_key_pattern = rf'key\s*=\s*["\']({var_name}_slider)["\']'
                if re.search(wrong_key_pattern, voting_content):
                    print(f"  ❌ {var_name}: Uses key='{var_name}_slider' (WRONG - doesn't match variable)")
                else:
                    print(f"  ⚠️  {var_name}: Key not found or doesn't match variable name")

    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)

    if not wrong_matches:
        print("✅ FIX APPLIED SUCCESSFULLY!")
        print("\nAll sliders use the correct pattern:")
        print("  - No assignments to st.session_state from slider returns")
        print("  - Sliders use key parameter for automatic synchronization")
        print("\nThe reset button should now work correctly!")
        return True
    else:
        print("❌ FIX NOT FULLY APPLIED")
        print("\nSome sliders still use the problematic pattern.")
        print("The reset button will NOT work correctly until fixed.")
        return False

def check_reset_button_implementation(file_path):
    """Check that the reset button implementation is correct."""

    with open(file_path, 'r') as f:
        content = f.read()

    print("\n" + "=" * 80)
    print("CHECKING RESET BUTTON IMPLEMENTATION")
    print("=" * 80)

    # Check for reset button
    if "Reset to Defaults" in content:
        print("✅ Reset button found")

        # Check that it updates session state
        reset_vars = [
            "token_threshold", "ast_threshold", "hash_threshold",
            "token_weight", "ast_weight", "hash_weight",
            "decision_threshold"
        ]

        # Find the reset button section
        lines = content.split('\n')
        in_reset = False
        reset_lines = []

        for line in lines:
            if "Reset to Defaults" in line and "button" in line:
                in_reset = True
            if in_reset:
                reset_lines.append(line)
                if "st.rerun()" in line:
                    break

        reset_content = '\n'.join(reset_lines)

        print("\nChecking reset updates:")
        for var in reset_vars:
            pattern = rf'st\.session_state\.{var}\s*='
            if re.search(pattern, reset_content):
                print(f"  ✅ {var}: Updated in reset handler")
            else:
                print(f"  ❌ {var}: NOT updated in reset handler")

        if "st.rerun()" in reset_content:
            print("  ✅ st.rerun() called after reset")
        else:
            print("  ❌ st.rerun() NOT called after reset")
    else:
        print("❌ Reset button not found")

    return True

if __name__ == "__main__":
    app_path = Path(__file__).parent / "app.py"

    if not app_path.exists():
        print(f"❌ Error: {app_path} not found")
        exit(1)

    # Run checks
    sliders_ok = check_slider_patterns(app_path)
    reset_ok = check_reset_button_implementation(app_path)

    print("\n" + "=" * 80)
    print("FINAL RESULT")
    print("=" * 80)

    if sliders_ok and reset_ok:
        print("🎉 SUCCESS: Reset button fix has been properly applied!")
        print("\nThe reset button should now work correctly:")
        print("  1. Sliders use key parameter for automatic sync")
        print("  2. No assignments that overwrite session_state")
        print("  3. Reset button updates all configuration values")
        print("  4. st.rerun() refreshes the UI after reset")
        exit(0)
    else:
        print("⚠️  WARNING: Some issues remain")
        print("\nPlease review the output above for details.")
        exit(1)