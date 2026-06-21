#====================================================================================================
# START - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

# THIS SECTION CONTAINS CRITICAL TESTING INSTRUCTIONS FOR BOTH AGENTS
# BOTH MAIN_AGENT AND TESTING_AGENT MUST PRESERVE THIS ENTIRE BLOCK

# Communication Protocol:
# If the `testing_agent` is available, main agent should delegate all testing tasks to it.
#
# You have access to a file called `test_result.md`. This file contains the complete testing state
# and history, and is the primary means of communication between main and the testing agent.
#
# Main and testing agents must follow this exact format to maintain testing data. 
# The testing data must be entered in yaml format Below is the data structure:
# 
## user_problem_statement: "تحديث حاسبة الميراث الإسلامي لعرض التفاصيل الكاملة: الفرض الأصلي، الرد، النسبة الشرعية، النسبة النهائية، ونوع الاستحقاق (فرض/فرض+رد/تعصيب)" {problem_statement}
## backend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.py"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## frontend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.js"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 0
##   run_ui: false
##
## test_plan:
##   current_focus:
##     - "Task name 1"
##     - "Task name 2"
##   stuck_tasks:
##     - "Task name with persistent issues"
##   test_all: false
##   test_priority: "high_first"  # or "sequential" or "stuck_first"
##
## agent_communication:
##     -agent: "main"  # or "testing" or "user"
##     -message: "Communication message between agents"

# Protocol Guidelines for Main agent
#
# 1. Update Test Result File Before Testing:
#    - Main agent must always update the `test_result.md` file before calling the testing agent
#    - Add implementation details to the status_history
#    - Set `needs_retesting` to true for tasks that need testing
#    - Update the `test_plan` section to guide testing priorities
#    - Add a message to `agent_communication` explaining what you've done
#
# 2. Incorporate User Feedback:
#    - When a user provides feedback that something is or isn't working, add this information to the relevant task's status_history
#    - Update the working status based on user feedback
#    - If a user reports an issue with a task that was marked as working, increment the stuck_count
#    - Whenever user reports issue in the app, if we have testing agent and task_result.md file so find the appropriate task for that and append in status_history of that task to contain the user concern and problem as well 
#
# 3. Track Stuck Tasks:
#    - Monitor which tasks have high stuck_count values or where you are fixing same issue again and again, analyze that when you read task_result.md
#    - For persistent issues, use websearch tool to find solutions
#    - Pay special attention to tasks in the stuck_tasks list
#    - When you fix an issue with a stuck task, don't reset the stuck_count until the testing agent confirms it's working
#
# 4. Provide Context to Testing Agent:
#    - When calling the testing agent, provide clear instructions about:
#      - Which tasks need testing (reference the test_plan)
#      - Any authentication details or configuration needed
#      - Specific test scenarios to focus on
#      - Any known issues or edge cases to verify
#
# 5. Call the testing agent with specific instructions referring to test_result.md
#
# IMPORTANT: Main agent must ALWAYS update test_result.md BEFORE calling the testing agent, as it relies on this file to understand what to test next.

#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================



#====================================================================================================
# Testing Data - Main Agent and testing sub agent both should log testing data below this section
#====================================================================================================

user_problem_statement: "تحديث حاسبة الميراث الإسلامي لعرض التفاصيل الكاملة: الفرض الأصلي (base_share_fraction)، النسبة الشرعية بالعربية (base_share_arabic)، الرد (radd_fraction)، النسبة النهائية (final_share_fraction)، ونوع الاستحقاق (share_type: فرض/فرض+رد/تعصيب). يجب أن تظهر هذه الحقول في: 1) API response من endpoint calculate-beneficiaries 2) جدول الحاسبة في InheritanceCalculatorDialog.js 3) جدول استمارة بحث الحالة (caseform_html.py)"

backend:
  - task: "Inheritance Calculator - Updated Models (AidBeneficiary)"
    implemented: true
    working: "NA"
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "تم تحديث نموذج AidBeneficiary في server.py (السطور 608-622) لإضافة الحقول الجديدة: base_share_fraction, base_share_arabic, radd_fraction, final_share_fraction, share_type. تم الحفاظ على الحقول القديمة (percentage, inheritance_type) للتوافق مع الكود القديم."

  - task: "Inheritance Calculator - Logic Update (calculate_inheritance)"
    implemented: true
    working: "NA"
    file: "/app/backend/services/inheritance_calculator.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "تم تحديث منطق حساب الميراث: 1) تم تصحيح المنطق للتمييز بين وجود أبناء ذكور (تعصيب) ووجود بنات فقط (فرض+رد). 2) تم تحديث دالة _convert_to_amounts لإرجاع الحقول الجديدة بشكل صحيح. 3) تم اختبار الحالات التالية بنجاح: (أ) زوجة + 4 بنات = فرض+رد ✓ (ب) زوج + أم + بنت = فرض+رد ✓ (ج) زوجة + ابن + ابنتان = تعصيب ✓"

  - task: "Case Form HTML - Updated Beneficiaries Table"
    implemented: true
    working: "NA"
    file: "/app/backend/services/caseform_html.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "تم تحديث جدول المستحقين في استمارة بحث الحالة: 1) إضافة أعمدة جديدة: النسبة الشرعية، النسبة الرقمية، نوع الاستحقاق 2) تم تحديث logic لعرض 'ثلثان + رد' بدلاً من الكسر النهائي فقط عندما يكون هناك رد 3) تم تعديل عرض الأعمدة في الجدول (thead + tbody)"

frontend:
  - task: "Inheritance Calculator Dialog - Updated UI Table"
    implemented: true
    working: "NA"
    file: "/app/frontend/src/components/InheritanceCalculatorDialog.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "تم تحديث واجهة الحاسبة لعرض الأعمدة الجديدة: 1) الفرض الأصلي (base_share_fraction) 2) النسبة الشرعية (base_share_arabic) 3) الرد (radd_fraction) 4) النسبة النهائية (final_share_fraction) 5) نوع الاستحقاق (share_type). تم تعديل الجدول في السطور 262-318 مع تحديث عدد الأعمدة من 7 إلى 9 أعمدة."

metadata:
  created_by: "main_agent"
  version: "2.0"
  test_sequence: 1
  run_ui: true

test_plan:
  current_focus:
    - "Inheritance Calculator - Logic Update (calculate_inheritance)"
    - "Inheritance Calculator Dialog - Updated UI Table"
    - "Case Form HTML - Updated Beneficiaries Table"
  stuck_tasks: []
  test_all: true
  test_priority: "high_first"

agent_communication:
  - agent: "main"
    message: "تم تنفيذ التحديثات المطلوبة على حاسبة الميراث. التعديلات شملت: (1) تحديث النماذج في server.py (2) تصحيح منطق الحساب في inheritance_calculator.py للتمييز الصحيح بين التعصيب (أبناء ذكور) والفرض+الرد (بنات فقط) (3) تحديث واجهة InheritanceCalculatorDialog.js لعرض 9 أعمدة بدلاً من 7 (4) تحديث جدول استمارة بحث الحالة في caseform_html.py. تم اختبار المنطق الرياضي بنجاح عبر Python CLI: حالة زوجة+4 بنات تعطي فرض+رد بشكل صحيح. يُرجى اختبار: (1) Backend API endpoint لحساب التوزيع (2) Frontend UI للتأكد من عرض الأعمدة الجديدة (3) استمارة بحث الحالة PDF/HTML"