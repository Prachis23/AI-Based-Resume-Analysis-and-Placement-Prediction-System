let testInterval; 

// --- 1. CORE FUNCTION: Switch Content Sections ---
function showContent(sectionId, clickedButton) {
    const displayArea = document.getElementById('course-content-display');
    let contentHTML = '';

    // Stop any running mock test timer
    if (typeof testInterval !== 'undefined') {
        clearInterval(testInterval);
    }

    // Handle Active Button Styling
    document.querySelectorAll('.nav-button').forEach(btn => {
        btn.classList.remove('active');
    });
    if (clickedButton) {
        clickedButton.classList.add('active');
    }

    // --- APTITUDE COURSES LIST (Expanded CareerRide Playlist) ---
    if (sectionId === 'aptitude') {
        contentHTML = `
            <h3>Comprehensive Aptitude Training (CareerRide Playlist)</h3>
            <div class="content-grid">
                
                <div class="course-card" onclick="loadVideo('Time & Work', 'https://www.youtube.com/embed/KE7tQf9spPg?autoplay=1')">
                    <h4>Quantitative Aptitude: Time & Work</h4>
                    <p>Start your placement journey with this fundamental topic.</p>
                    <p style="color:#007bff; font-weight:bold;">Click to Start Video →</p>
                </div>
                
                <div class="course-card" onclick="loadVideo('Logical Reasoning: Direction', 'https://www.youtube.com/embed/x0WkptLF6oE?autoplay=1')">
                    <h4>Logical Reasoning: Direction Sense</h4>
                    <p>Techniques to solve complex reasoning questions quickly.</p>
                    <p style="color:#007bff; font-weight:bold;">Click to Start Video →</p>
                </div>

                <div class="course-card" onclick="loadVideo('Permutations and Combinations', 'https://www.youtube-nocookie.com/embed/ETiRE7N7pEI?auyoplay=1')">
                    <h4>Advanced Quant: Permutations and Combinations</h4>
                    <p>Crucial topic for high-salary package companies.</p>
                    <p style="color:#007bff; font-weight:bold;">Click to Start Video →</p>
                </div>

                <div class="course-card" onclick="loadVideo('Data Interpretation', 'https://www.youtube-nocookie.com/embed/LEM2xQEVYGo?autoplay=1')">
                    <h4>Quantitative Aptitude: Data Interpretation (Tables & Graphs)</h4>
                    <p>Practice reading and analyzing charts and tables.</p>
                    <p style="color:#007bff; font-weight:bold;">Click to Start Video →</p>
                </div>

                <div class="course-card" onclick="loadVideo('Coding-Decoding', 'https://www.youtube-nocookie.com/embed/wwN3mJ-b4FY?autoplay=1')">
                    <h4>Logical Reasoning: Coding-Decoding</h4>
                    <p>Learn pattern recognition for letter and number sequences.</p>
                    <p style="color:#007bff; font-weight:bold;">Click to Start Video →</p>
                </div>
                
                <div class="course-card" onclick="loadVideo('Probability Basics', 'https://www.youtube-nocookie.com/embed/ximxxERGSUc?autoplay=1')">
                    <h4>Quantitative Aptitude: Probability</h4>
                    <p>Understanding concepts of sets, events, and chance.</p>
                    <p style="color:#007bff; font-weight:bold;">Click to Start Video →</p>
                </div>

            </div>`;
    } 
    
    // --- TECHNICAL COURSES LIST (Expanded Videos) ---
    else if (sectionId === 'technical') {
        contentHTML = `
            <h3>Core Technical Skills & Programming (Click a card to Watch)</h3>
            <div class="content-grid">
                
                <div class="course-card" onclick="loadVideo('Complete Python Course ', 'https://www.youtube-nocookie.com/embed/UrsmFxEIp5k?autoplay=1')">
                    <h4>Python Basics: Variables & Data Types</h4>
                    <p>Essential first lecture for learning Python from scratch.</p>
                    <p style="color:#007bff; font-weight:bold;">Click to Start Video →</p>
                </div>
                
                <div class="course-card" onclick="loadVideo('Data Structures - Array, Linked List, Stack, Queue ', 'https://www.youtube-nocookie.com/embed/i86Q5q_Po9Y?autoplay=1')">
                    <h4>Data Structures: Linked Lists</h4>
                    <p>Conceptual deep dive into Singly and Doubly Linked Lists.</p>
                    <p style="color:#007bff; font-weight:bold;">Click to Start Video →</p>
                </div>

                <div class="course-card" onclick="loadVideo('SQL Tutorial', 'https://www.youtube-nocookie.com/embed/yE6tIle64tU?autoplay=1')">
                    <h4>Database Management: Advanced SQL Joins</h4>
                    <p>Master INNER, LEFT, RIGHT, and FULL joins for technical interviews.</p>
                    <p style="color:#007bff; font-weight:bold;">Click to Start Video →</p>
                </div>

                <div class="course-card" onclick="loadVideo('Operating System', 'https://www.youtube-nocookie.com/embed/8XBtAjKwCm4?autoplay=1')">
                    <h4>Core CS: Operating System - Process Scheduling</h4>
                    <p>Learn about FCFS, SJF, and Round Robin algorithms.</p>
                    <p style="color:#007bff; font-weight:bold;">Click to Start Video →</p>
                </div>

            </div>`;
    } 
    
    // --- MOCK TESTS LIST ---
    else if (sectionId === 'mock-tests') {
        contentHTML = `
            <h3>Placement Mock Tests (Aptitude + Technical)</h3>
            <div class="test-list">
                <p style="background-color:#ffe0b2; padding:10px; border-left: 4px solid #ff9800; border-radius: 4px;">
                    ⚠️ **Important:** All tests have a strict timer. Do not refresh or close the window after starting!
                </p>
                
                <div class="course-card">
                    <h4>Mock Test 1: Full-Length Company Simulation</h4>
                    <p><strong>Sections:</strong> Quant, Reasoning, Coding (2) | <strong>Time:</strong> 90 Mins</p>
                    <button class="start-btn-inline" onclick="startMockTest(90)">Start Test (90 Mins)</button>
                </div>
                
                <div class="course-card">
                    <h4>Mock Test 2: Only Aptitude Speed Check</h4>
                    <p><strong>Sections:</strong> Quant, Reasoning | <strong>Time:</strong> 45 Mins</p>
                    <button class="start-btn-inline" onclick="startMockTest(45)">Start Test (45 Mins)</button>
                </div>
            </div>`;
    }

    displayArea.innerHTML = contentHTML;
}

// --- 2. FUNCTION: Load Video Player (Ensures Direct Start) ---
function loadVideo(title, embedUrl) {
    const displayArea = document.getElementById('course-content-display');
    
    if (typeof testInterval !== 'undefined') {
        clearInterval(testInterval);
    }

    displayArea.innerHTML = `
        <div class="video-player-container">
            <button class="back-btn" onclick="showContent(document.querySelector('.nav-button.active').dataset.section, document.querySelector('.nav-button.active'))">
                ← Back to Courses List
            </button>
            
            <h3 style="margin-top: 15px;">Currently Watching: ${title}</h3>
            
            <div class="video-responsive">
                <iframe 
                    src="${embedUrl}" 
                    frameborder="0" 
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                    allowfullscreen>
                </iframe>
            </div>
            
            <p style="margin-top: 20px; padding: 10px; border-left: 3px solid #007bff; background-color: #e9f5ff;">
                Remember to take notes! This lesson is crucial for the next module.
            </p>
        </div>
    `;
}

// --- 3. FUNCTION: Start Mock Test (with Timer) ---
function startMockTest(durationMinutes) {
    const displayArea = document.getElementById('course-content-display');
    const totalSeconds = durationMinutes * 60;
    let secondsRemaining = totalSeconds;

    // Display the Test Interface (Simplified)
    displayArea.innerHTML = `
        <div class="mock-test-interface">
            <h2>Test in Progress... ⚠️</h2>
            <div id="test-timer" style="font-size: 2.5em; color: red; margin: 15px 0; font-weight: bold;">Time Remaining: 00:00</div>
            
            <div style="border: 1px solid #ccc; padding: 15px; margin-bottom: 15px; background-color: white; border-radius: 4px;">
                <p>Q1. (Aptitude): A train 150m long is traveling at 54 km/hr. How long will it take to pass a pole?</p>
                <input type="text" placeholder="Enter time in seconds" style="padding: 8px; width: 90%; border: 1px solid #ddd; border-radius: 4px;">
            </div>

            <div style="border: 1px solid #ccc; padding: 15px; margin-bottom: 15px; background-color: white; border-radius: 4px;">
                <p>Q2. (Technical): Which data structure is FIFO (First-In, First-Out)?</p>
                <label><input type="radio" name="q2"> Stack</label><br>
                <label><input type="radio" name="q2"> Queue</label><br>
                <label><input type="radio" name="q2"> Array</label>
            </div>
            
            <button onclick="endTest()" style="padding: 12px 25px; background-color: #dc3545; color: white; border: none; border-radius: 5px; margin-top: 20px; font-weight: bold;">Submit Test</button>
        </div>
    `;

    // Start the Timer
    clearInterval(testInterval); 
    testInterval = setInterval(() => {
        secondsRemaining--;

        const minutes = Math.floor(secondsRemaining / 60);
        const seconds = secondsRemaining % 60;

        const timeString = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        document.getElementById('test-timer').textContent = `Time Remaining: ${timeString}`;

        if (secondsRemaining <= 0) {
            clearInterval(testInterval);
            alert("Time's up! The test has been automatically submitted.");
            endTest();
        }
    }, 1000); 
}

// --- 4. FUNCTION: End Test ---
function endTest() {
    clearInterval(testInterval);
    const displayArea = document.getElementById('course-content-display');
    
    displayArea.innerHTML = `
        <div style="text-align: center; padding: 50px; background-color: #e9ecef; border-radius: 8px;">
            <h2>Test Submitted Successfully! 🎉</h2>
            <p>Your results are being processed. Score: **1/2 (Simulated)**</p>
            <p>Detailed sectional analysis will be available on your dashboard.</p>
            <button onclick="showContent('mock-tests', document.querySelector('.nav-button[data-section=\'mock-tests\']'))" 
                    style="margin-top: 20px; padding: 12px 25px; background-color: #007bff; color: white; border: none; border-radius: 5px; font-weight: bold;">
                Go Back to Mock Tests
            </button>
        </div>
    `;
    
    document.querySelectorAll('.nav-button').forEach(btn => btn.classList.remove('active'));
    document.querySelector('.nav-button[data-section=\'mock-tests\']').classList.add('active');
}


// --- 5. INITIAL LOAD: Show Aptitude on startup ---
window.onload = () => {
    const defaultButton = document.querySelector('.nav-button[data-section=\'aptitude\']');
    if (defaultButton) {
        showContent('aptitude', defaultButton);
    }
};