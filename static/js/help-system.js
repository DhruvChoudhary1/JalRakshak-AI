// Help System and Onboarding Functions

// Initialize help system
function initializeHelpSystem() {
    const helpBtn = document.getElementById('helpBtn');
    const closeHelp = document.getElementById('closeHelp');
    const startTour = document.getElementById('startTour');
    const helpNavBtns = document.querySelectorAll('.help-nav-btn');
    
    // Help button click
    if (helpBtn) {
        helpBtn.addEventListener('click', showHelpModal);
    }
    
    // Close help modal
    if (closeHelp) {
        closeHelp.addEventListener('click', hideHelpModal);
    }
    
    // Start tour button
    if (startTour) {
        startTour.addEventListener('click', function() {
            hideHelpModal();
            startInteractiveTour();
        });
    }
    
    // Help navigation
    helpNavBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const section = this.getAttribute('data-section');
            showHelpSection(section);
            
            // Update active button
            helpNavBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
        });
    });
    
    // Close modal on outside click
    const helpModal = document.getElementById('helpModal');
    if (helpModal) {
        helpModal.addEventListener('click', function(e) {
            if (e.target === this) {
                hideHelpModal();
            }
        });
    }
}

// Show help modal
function showHelpModal() {
    const helpModal = document.getElementById('helpModal');
    if (helpModal) {
        helpModal.style.display = 'flex';
        showHelpSection('helpIntro');
    }
}

// Hide help modal
function hideHelpModal() {
    const helpModal = document.getElementById('helpModal');
    if (helpModal) {
        helpModal.style.display = 'none';
        
        // Save preference if checkbox is checked
        const dontShowAgain = document.getElementById('dontShowAgain');
        if (dontShowAgain && dontShowAgain.checked) {
            localStorage.setItem('ingres_hide_onboarding', 'true');
        }
    }
}

// Show specific help section
function showHelpSection(sectionId) {
    // Hide all sections
    const sections = document.querySelectorAll('.help-section');
    sections.forEach(section => {
        section.classList.remove('active');
    });
    
    // Show target section
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.classList.add('active');
    }
}

// Check if first-time user
function checkFirstTimeUser() {
    const hideOnboarding = localStorage.getItem('ingres_hide_onboarding');
    const hasVisited = localStorage.getItem('ingres_has_visited');
    
    if (!hideOnboarding && !hasVisited) {
        // Show onboarding after a short delay
        setTimeout(() => {
            showHelpModal();
        }, 1500);
        
        localStorage.setItem('ingres_has_visited', 'true');
    }
}

// Interactive tour functionality
function startInteractiveTour() {
    // Create tour backdrop
    const backdrop = document.createElement('div');
    backdrop.id = 'tourBackdrop';
    backdrop.className = 'tour-backdrop';
    document.body.appendChild(backdrop);
    const tourSteps = [
        {
            element: '#chatInput',
            title: '💬 Chat Interface',
            content: 'Type your questions here. Ask about water levels, quality, or predictions in natural language.',
            position: 'top'
        },
        {
            element: '#quickActions',
            title: '🎯 Quick Actions',
            content: 'Use these buttons for common queries. They\'ll help you get started quickly.',
            position: 'top'
        },
        {
            element: '#voiceBtn',
            title: '🎤 Voice Input',
            content: 'Click here to speak your questions. Supports 22+ Indian languages.',
            position: 'top'
        },
        {
            element: '#crisisBtn', // Updated from .control-buttons to #crisisBtn
            title: '🛠️ Smart Features',
            content: 'Access crisis prediction, interactive maps, water game, and more advanced features.',
            position: 'bottom'
        },
        {
            element: '#languageSelect',
            title: '🌐 Language Support',
            content: 'Switch between different Indian languages for a localized experience.',
            position: 'bottom'
        }
    ];
    
    let currentStep = 0;
    
    function showTourStep(stepIndex) {
        // Remove existing tooltip
        const existingTooltip = document.getElementById('currentTourTooltip');
        if (existingTooltip) {
            existingTooltip.remove();
        }
        
        if (stepIndex >= tourSteps.length) {
            endTour();
            return;
        }
        
        currentStep = stepIndex;
        const step = tourSteps[stepIndex];
        const element = document.querySelector(step.element);
        
        if (!element) {
            // Skip this step if element not found
            showTourStep(stepIndex + 1);
            return;
        }
        
        // Create tour tooltip
        const tooltip = createTourTooltip(step, stepIndex, tourSteps.length);
        document.body.appendChild(tooltip);
        
        // Position tooltip after a brief delay to ensure proper rendering
        setTimeout(() => {
            positionTooltip(tooltip, element, step.position);
        }, 50);
        
        // Highlight element
        highlightElement(element);
        
        // Scroll element into view
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    
    function createTourTooltip(step, index, total) {
        const tooltip = document.createElement('div');
        tooltip.className = 'tour-tooltip';
        tooltip.id = 'currentTourTooltip';
        tooltip.innerHTML = `
            <div class="tour-header">
                <h4>${step.title}</h4>
                <span class="tour-progress">${index + 1}/${total}</span>
            </div>
            <p>${step.content}</p>
            <div class="tour-actions">
                <button class="tour-btn tour-skip" id="tourSkipBtn">Skip Tour</button>
                <div class="tour-nav">
                    ${index > 0 ? '<button class="tour-btn tour-prev" id="tourPrevBtn">Previous</button>' : ''}
                    <button class="tour-btn tour-next" id="tourNextBtn">${index === total - 1 ? 'Finish' : 'Next'}</button>
                </div>
            </div>
        `;
        
        // Add event listeners after creating the tooltip
        setTimeout(() => {
            const skipBtn = document.getElementById('tourSkipBtn');
            const prevBtn = document.getElementById('tourPrevBtn');
            const nextBtn = document.getElementById('tourNextBtn');
            
            if (skipBtn) {
                skipBtn.addEventListener('click', () => endTour());
            }
            if (prevBtn) {
                prevBtn.addEventListener('click', () => showTourStep(index - 1));
            }
            if (nextBtn) {
                nextBtn.addEventListener('click', () => showTourStep(index + 1));
            }
        }, 100);
        
        return tooltip;
    }
    
    function positionTooltip(tooltip, element, position) {
        const rect = element.getBoundingClientRect();
        const tooltipRect = tooltip.getBoundingClientRect();
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;
        
        let top, left;
        
        switch (position) {
            case 'top':
                top = rect.top - tooltipRect.height - 15;
                left = rect.left + (rect.width - tooltipRect.width) / 2;
                break;
            case 'bottom':
                top = rect.bottom + 15;
                left = rect.left + (rect.width - tooltipRect.width) / 2;
                break;
            case 'left':
                top = rect.top + (rect.height - tooltipRect.height) / 2;
                left = rect.left - tooltipRect.width - 15;
                break;
            case 'right':
                top = rect.top + (rect.height - tooltipRect.height) / 2;
                left = rect.right + 15;
                break;
            default:
                top = rect.bottom + 15;
                left = rect.left;
        }
        
        // Smart positioning to avoid viewport edges
        if (left < 20) {
            left = 20;
        } else if (left + tooltipRect.width > viewportWidth - 20) {
            left = viewportWidth - tooltipRect.width - 20;
        }
        
        if (top < 20) {
            top = rect.bottom + 15; // Move below if too high
        } else if (top + tooltipRect.height > viewportHeight - 20) {
            top = rect.top - tooltipRect.height - 15; // Move above if too low
        }
        
        // Final boundary check
        top = Math.max(20, Math.min(top, viewportHeight - tooltipRect.height - 20));
        left = Math.max(20, Math.min(left, viewportWidth - tooltipRect.width - 20));
        
        tooltip.style.position = 'fixed';
        tooltip.style.top = top + 'px';
        tooltip.style.left = left + 'px';
        tooltip.style.zIndex = '3000';
    }
    
    function highlightElement(element) {
        // Remove previous highlights
        document.querySelectorAll('.tour-highlight').forEach(el => {
            el.classList.remove('tour-highlight');
        });
        
        // Add highlight to current element
        element.classList.add('tour-highlight');
    }
    
    function endTour() {
        // Remove all tour elements
        document.querySelectorAll('.tour-tooltip').forEach(tooltip => {
            tooltip.remove();
        });
        
        const currentTooltip = document.getElementById('currentTourTooltip');
        if (currentTooltip) {
            currentTooltip.remove();
        }
        
        // Remove backdrop
        const backdrop = document.getElementById('tourBackdrop');
        if (backdrop) {
            backdrop.remove();
        }
        
        // Remove highlights
        document.querySelectorAll('.tour-highlight').forEach(el => {
            el.classList.remove('tour-highlight');
        });
        
        // Show completion message
        showTourCompletionMessage();
    }
    
    function showTourCompletionMessage() {
        const chatContainer = document.getElementById('chatContainer');
        if (chatContainer) {
            const completionMessage = document.createElement('div');
            completionMessage.className = 'message bot-message tour-completion';
            completionMessage.innerHTML = `
                <div class="message-avatar">🎉</div>
                <div class="message-content">
                    <div class="message-header">
                        <span class="sender-name">INGRES AI</span>
                        <span class="message-time">${new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}</span>
                    </div>
                    <p><strong>🎉 Tour Complete!</strong></p>
                    <p>You're all set to explore INGRES AI! Try asking me about water levels in your area or use the quick action buttons below.</p>
                    <p><em>💡 Tip: You can always click the ❓ button for help anytime.</em></p>
                </div>
            `;
            chatContainer.appendChild(completionMessage);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    }
    
    // Make functions globally accessible for onclick handlers
    window.showTourStep = showTourStep;
    window.endTour = endTour;
    
    // Start the tour
    showTourStep(0);
}

document.addEventListener('DOMContentLoaded', function() {
    initializeHelpSystem();
    // Show help modal and tour only for first-time users
    const hideOnboarding = localStorage.getItem('ingres_hide_onboarding');
    const hasVisited = localStorage.getItem('ingres_has_visited');
    if (!hideOnboarding && !hasVisited) {
        setTimeout(function() {
            showHelpModal();
            startInteractiveTour();
        }, 1200);
        localStorage.setItem('ingres_has_visited', 'true');
    }
});