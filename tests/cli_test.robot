*** Settings ***
Library    Process

*** Variables ***
${ROOT}    ${CURDIR}/..
${AUTOMATION_SCRIPT}    ${ROOT}/scripts/automation.py
${ASYNC_SCRIPT}    ${ROOT}/scripts/async_automation.py

*** Test Cases ***
Run Automation Script
    [Documentation]    Run the synchronous automation script and verify it succeeds.
    ${result}=    Run Process    python    ${AUTOMATION_SCRIPT}    cwd=${ROOT}    stdout=PIPE    stderr=PIPE
    Should Be Equal As Integers    ${result.rc}    0
    Log Many    ${result.stdout}
    Log Many    ${result.stderr}

Run Async Automation Script
    [Documentation]    Run the asynchronous automation script and verify it succeeds.
    ${result}=    Run Process    python    ${ASYNC_SCRIPT}    cwd=${ROOT}    stdout=PIPE    stderr=PIPE
    Should Be Equal As Integers    ${result.rc}    0
    Log Many    ${result.stdout}
    Log Many    ${result.stderr}

Validate NPM Lint Workflow
    [Documentation]    Validate the frontend lint command.
    ${result}=    Run Process    npm    run    lint    cwd=${ROOT}    stdout=PIPE    stderr=PIPE
    Should Be Equal As Integers    ${result.rc}    0

Validate NPM Build Workflow
    [Documentation]    Validate the frontend build command.
    ${result}=    Run Process    npm    run    build    cwd=${ROOT}    stdout=PIPE    stderr=PIPE
    Should Be Equal As Integers    ${result.rc}    0

Validate NPM Test Workflow
    [Documentation]    Validate the frontend test command.
    ${result}=    Run Process    npm    test    cwd=${ROOT}    stdout=PIPE    stderr=PIPE
    Should Be Equal As Integers    ${result.rc}    0

Validate Git Status Command
    [Documentation]    Validate the repository git status command.
    ${result}=    Run Process    git    status    cwd=${ROOT}    stdout=PIPE    stderr=PIPE
    Should Be Equal As Integers    ${result.rc}    0

Validate Backend Source Compilation
    [Documentation]    Verify backend Python source compiles successfully.
    ${result}=    Run Process    python    -m    py_compile    backend/backend/app.py    cwd=${ROOT}    stdout=PIPE    stderr=PIPE
    Should Be Equal As Integers    ${result.rc}    0
