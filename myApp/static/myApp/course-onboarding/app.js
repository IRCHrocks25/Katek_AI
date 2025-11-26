// State management
let currentStep = 1;
const totalSteps = 12;
const state = {};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadState();
    initializeStepNavigation();
    initializeInteractions();
    updateProgress();
    updateStepVisibility();
});

// Step Navigation
function initializeStepNavigation() {
    const nextBtn = document.getElementById('next-btn');
    const backBtn = document.getElementById('back-btn');
    const saveExitBtn = document.getElementById('save-exit-btn');

    nextBtn.addEventListener('click', () => {
        if (validateStep(currentStep)) {
            if (currentStep < totalSteps) {
                currentStep++;
                updateStepVisibility();
                updateProgress();
                saveState();
            } else {
                submitForm();
            }
        }
    });

    backBtn.addEventListener('click', () => {
        if (currentStep > 1) {
            currentStep--;
            updateStepVisibility();
            updateProgress();
            saveState();
        }
    });

    saveExitBtn.addEventListener('click', () => {
        saveState();
        alert('Progress saved! You can continue later.');
    });

    // Step navigation from sidebar
    document.querySelectorAll('.step-nav-item').forEach((item, index) => {
        item.addEventListener('click', () => {
            const targetStep = index + 1;
            if (targetStep <= currentStep) {
                currentStep = targetStep;
                updateStepVisibility();
                updateProgress();
                saveState();
            }
        });
    });
}

function updateStepVisibility() {
    document.querySelectorAll('.step-container').forEach((step, index) => {
        if (index + 1 === currentStep) {
            step.classList.remove('hidden');
            step.classList.add('animate-fade-in');
        } else {
            step.classList.add('hidden');
            step.classList.remove('animate-fade-in');
        }
    });

    // Update navigation buttons
    const backBtn = document.getElementById('back-btn');
    const nextBtn = document.getElementById('next-btn');

    if (currentStep === 1) {
        backBtn.classList.add('hidden');
    } else {
        backBtn.classList.remove('hidden');
    }

    if (currentStep === totalSteps) {
        nextBtn.innerHTML = 'Finish & Submit <i class="fas fa-check"></i>';
    } else {
        nextBtn.innerHTML = 'Next <i class="fas fa-arrow-right"></i>';
    }

    // Update sidebar
    document.querySelectorAll('.step-nav-item').forEach((item, index) => {
        const stepNum = index + 1;
        const icon = item.querySelector('i');
        
        if (stepNum < currentStep) {
            item.classList.remove('text-slate-500', 'bg-slate-800/50');
            item.classList.add('text-emerald-400');
            icon.className = 'fas fa-check w-5 text-center';
        } else if (stepNum === currentStep) {
            item.classList.remove('text-slate-500', 'text-emerald-400');
            item.classList.add('text-slate-50', 'font-semibold', 'bg-slate-800/50');
            // Restore original icon
            const icons = ['fa-user', 'fa-lightbulb', 'fa-bullseye', 'fa-folder-open', 'fa-palette', 
                         'fa-sitemap', 'fa-video', 'fa-gavel', 'fa-dollar-sign', 'fa-calendar-alt', 
                         'fa-comments', 'fa-upload'];
            icon.className = `fas ${icons[index]} w-5 text-center`;
        } else {
            item.classList.remove('text-emerald-400', 'text-slate-50', 'font-semibold', 'bg-slate-800/50');
            item.classList.add('text-slate-500');
        }
    });
}

function updateProgress() {
    const progress = (currentStep / totalSteps) * 100;
    document.getElementById('progress-bar').style.width = `${progress}%`;
    document.getElementById('progress-text').textContent = `Step ${currentStep} of ${totalSteps}`;
}

// Validation
function validateStep(step) {
    const stepContainer = document.querySelector(`[data-step="${step}"]`);
    const requiredFields = stepContainer.querySelectorAll('[required]');
    let isValid = true;

    requiredFields.forEach(field => {
        if (field.type === 'hidden') {
            if (!field.value || field.value === '') {
                isValid = false;
                showError(field, 'This field is required');
            } else {
                clearError(field);
            }
        } else if (field.type === 'radio' || field.type === 'checkbox') {
            const name = field.name;
            const checked = stepContainer.querySelector(`[name="${name}"]:checked`);
            if (!checked) {
                isValid = false;
                showError(field, 'Please select an option');
            } else {
                clearError(field);
            }
        } else {
            if (!field.value.trim()) {
                isValid = false;
                showError(field, 'This field is required');
            } else {
                clearError(field);
            }
        }
    });

    return isValid;
}

function showError(field, message) {
    clearError(field);
    const errorDiv = document.createElement('p');
    errorDiv.className = 'text-red-400 text-xs mt-1 error-message';
    errorDiv.textContent = message;
    field.parentElement.appendChild(errorDiv);
    field.classList.add('border-red-500');
}

function clearError(field) {
    const errorMsg = field.parentElement.querySelector('.error-message');
    if (errorMsg) errorMsg.remove();
    field.classList.remove('border-red-500');
}

// Initialize all interactive elements
function initializeInteractions() {
    // Step 1: Channel pills
    initializeChannelPills();
    
    // Step 2: Level buttons, description counter, duration helper
    initializeLevelButtons();
    initializeDescriptionCounter();
    initializeDurationHelper();
    
    // Step 3: Outcomes, skills, certification
    initializeOutcomes();
    initializeSkills();
    initializeCertification();
    
    // Step 4: Content types, expandable sections
    initializeContentTypes();
    initializeExpandableSections();
    
    // Step 5: Tone chips, style URLs, format cards
    initializeToneChips();
    initializeStyleUrls();
    initializeFormatCards();
    
    // Step 6: Structure, activities, quiz slider
    initializeActivities();
    initializeQuizSlider();
    
    // Step 8: Ownership toggle
    initializeOwnershipToggle();
    
    // Step 9: Hosting, access model, integrations, analytics
    initializeHosting();
    initializeAccessModel();
    initializeIntegrations();
    initializeAnalytics();
    
    // Step 10: Priorities
    initializePriorities();
    
    // Step 11: Decision makers, feedback speed
    initializeDecisionMakers();
    initializeFeedbackSpeed();
    
    // Success modal
    initializeModal();
}

// Step 1: Channel Pills
function initializeChannelPills() {
    document.querySelectorAll('.channel-pill').forEach(pill => {
        pill.addEventListener('click', () => {
            document.querySelectorAll('.channel-pill').forEach(p => {
                p.classList.remove('bg-emerald-500/10', 'border-emerald-400', 'text-emerald-300');
            });
            pill.classList.add('bg-emerald-500/10', 'border-emerald-400', 'text-emerald-300');
            document.querySelector('[name="preferred_channel"]').value = pill.dataset.value;
        });
    });
}

// Step 2: Level Buttons
function initializeLevelButtons() {
    const helperTexts = {
        beginner: "We'll keep things simple, clear, and step-by-step.",
        intermediate: "Perfect for those ready to level up their skills.",
        advanced: "We'll dive deep into complex concepts and advanced techniques."
    };

    document.querySelectorAll('.level-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.level-btn').forEach(b => {
                b.classList.remove('bg-emerald-500/10', 'border-emerald-400', 'text-emerald-300');
            });
            btn.classList.add('bg-emerald-500/10', 'border-emerald-400', 'text-emerald-300');
            document.querySelector('[name="course_level"]').value = btn.dataset.value;
            
            const helper = document.getElementById('level-helper');
            helper.textContent = helperTexts[btn.dataset.value];
            helper.classList.remove('hidden');
        });
    });
}

function initializeDescriptionCounter() {
    const textarea = document.querySelector('[name="course_description"]');
    const counter = document.getElementById('desc-counter');
    if (textarea && counter) {
        textarea.addEventListener('input', () => {
            counter.textContent = textarea.value.length;
        });
    }
}

function initializeDurationHelper() {
    const modules = document.querySelector('[name="modules"]');
    const lessons = document.querySelector('[name="lessons_per_module"]');
    const helper = document.getElementById('duration-helper');
    
    function updateHelper() {
        const mods = parseInt(modules.value) || 0;
        const less = parseInt(lessons.value) || 0;
        if (mods > 0 && less > 0) {
            const total = mods * less;
            helper.textContent = `Roughly ${total} bite-sized lessons total.`;
        } else {
            helper.textContent = '';
        }
    }
    
    if (modules) modules.addEventListener('input', updateHelper);
    if (lessons) lessons.addEventListener('input', updateHelper);
}

// Step 3: Outcomes
function initializeOutcomes() {
    const addBtn = document.getElementById('add-outcome');
    if (addBtn) {
        addBtn.addEventListener('click', () => {
            const list = document.getElementById('outcomes-list');
            const template = list.querySelector('.outcome-item').cloneNode(true);
            const input = template.querySelector('input');
            input.value = '';
            input.placeholder = `Outcome ${list.children.length + 1}`;
            list.appendChild(template);
        });
    }
}

// Step 3: Skills
function initializeSkills() {
    const input = document.getElementById('skill-input');
    const container = document.getElementById('skills-container');
    
    if (input && container) {
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && input.value.trim()) {
                e.preventDefault();
                const skill = input.value.trim();
                const pill = document.createElement('span');
                pill.className = 'inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-400/50 text-emerald-300 text-sm';
                pill.innerHTML = `${skill} <button type="button" class="remove-skill ml-1 hover:text-emerald-100"><i class="fas fa-times"></i></button>`;
                
                pill.querySelector('.remove-skill').addEventListener('click', () => {
                    pill.remove();
                });
                
                container.appendChild(pill);
                input.value = '';
            }
        });
    }
}

// Step 3: Certification
function initializeCertification() {
    document.querySelectorAll('.cert-toggle').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.cert-toggle').forEach(b => {
                b.classList.remove('bg-emerald-500/10', 'border-emerald-400', 'text-emerald-300');
            });
            btn.classList.add('bg-emerald-500/10', 'border-emerald-400', 'text-emerald-300');
            document.querySelector('[name="certification"]').value = btn.dataset.value;
            
            const details = document.getElementById('cert-details');
            if (btn.dataset.value === 'yes') {
                details.classList.remove('hidden');
            } else {
                details.classList.add('hidden');
            }
        });
    });
}

// Step 4: Content Types
function initializeContentTypes() {
    document.querySelectorAll('.content-type-card').forEach(card => {
        card.addEventListener('click', () => {
            card.classList.toggle('ring-2');
            card.classList.toggle('ring-emerald-400');
            card.classList.toggle('border-emerald-400');
            
            updateContentTypesValue();
        });
    });
}

function updateContentTypesValue() {
    const selected = Array.from(document.querySelectorAll('.content-type-card.ring-2'))
        .map(card => card.dataset.value);
    document.querySelector('[name="existing_content_types"]').value = selected.join(',');
}

// Step 4: Expandable Sections
function initializeExpandableSections() {
    const mustIncludeBtn = document.getElementById('toggle-must-include');
    const mustIncludeSection = document.getElementById('must-include-section');
    const topicsAvoidBtn = document.getElementById('toggle-topics-avoid');
    const topicsAvoidSection = document.getElementById('topics-avoid-section');
    
    if (mustIncludeBtn && mustIncludeSection) {
        mustIncludeBtn.addEventListener('click', () => {
            mustIncludeSection.classList.toggle('hidden');
            const icon = mustIncludeBtn.querySelector('i');
            icon.classList.toggle('fa-plus');
            icon.classList.toggle('fa-minus');
        });
    }
    
    if (topicsAvoidBtn && topicsAvoidSection) {
        topicsAvoidBtn.addEventListener('click', () => {
            topicsAvoidSection.classList.toggle('hidden');
            const icon = topicsAvoidBtn.querySelector('i');
            icon.classList.toggle('fa-plus');
            icon.classList.toggle('fa-minus');
        });
    }
}

// Step 5: Tone Chips
function initializeToneChips() {
    document.querySelectorAll('.tone-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            chip.classList.toggle('bg-emerald-500/10');
            chip.classList.toggle('border-emerald-400');
            chip.classList.toggle('text-emerald-300');
            
            updateToneValue();
        });
    });
}

function updateToneValue() {
    const selected = Array.from(document.querySelectorAll('.tone-chip.bg-emerald-500\\/10'))
        .map(chip => chip.dataset.value);
    document.querySelector('[name="tone"]').value = selected.join(',');
}

// Step 5: Style URLs
function initializeStyleUrls() {
    const addBtn = document.getElementById('add-style-url');
    if (addBtn) {
        addBtn.addEventListener('click', () => {
            const list = document.getElementById('style-urls-list');
            const template = list.querySelector('input').cloneNode(true);
            template.value = '';
            list.appendChild(template);
        });
    }
}

// Step 5: Format Cards
function initializeFormatCards() {
    document.querySelectorAll('.format-card').forEach(card => {
        card.addEventListener('click', () => {
            card.classList.toggle('ring-2');
            card.classList.toggle('ring-emerald-400');
            card.classList.toggle('border-emerald-400');
            
            updateFormatValue();
        });
    });
}

function updateFormatValue() {
    const selected = Array.from(document.querySelectorAll('.format-card.ring-2'))
        .map(card => card.dataset.value);
    document.querySelector('[name="formatting_preferences"]').value = selected.join(',');
}

// Step 6: Activities
function initializeActivities() {
    document.querySelectorAll('.activity-card').forEach(card => {
        card.addEventListener('click', () => {
            card.classList.toggle('ring-2');
            card.classList.toggle('ring-emerald-400');
            card.classList.toggle('border-emerald-400');
            
            updateActivitiesValue();
        });
    });
}

function updateActivitiesValue() {
    const selected = Array.from(document.querySelectorAll('.activity-card.ring-2'))
        .map(card => card.dataset.value);
    document.querySelector('[name="activities"]').value = selected.join(',');
}

// Step 6: Quiz Slider
function initializeQuizSlider() {
    const slider = document.getElementById('quiz-slider');
    const counter = document.getElementById('quiz-count');
    const hidden = document.querySelector('[name="quiz_count"]');
    
    if (slider && counter && hidden) {
        slider.addEventListener('input', () => {
            counter.textContent = slider.value;
            hidden.value = slider.value;
        });
    }
}

// Step 8: Ownership Toggle
function initializeOwnershipToggle() {
    document.querySelectorAll('.ownership-toggle').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.ownership-toggle').forEach(b => {
                b.classList.remove('bg-emerald-500/10', 'border-emerald-400', 'text-emerald-300');
            });
            btn.classList.add('bg-emerald-500/10', 'border-emerald-400', 'text-emerald-300');
            document.querySelector('[name="ownership_rights"]').value = btn.dataset.value;
            
            const explanation = document.getElementById('ownership-explanation');
            if (btn.dataset.value === 'no') {
                explanation.classList.remove('hidden');
            } else {
                explanation.classList.add('hidden');
            }
        });
    });
}

// Step 9: Hosting
function initializeHosting() {
    document.querySelectorAll('.hosting-card').forEach(card => {
        card.addEventListener('click', () => {
            document.querySelectorAll('.hosting-card').forEach(c => {
                c.classList.remove('ring-2', 'ring-emerald-400', 'border-emerald-400');
            });
            card.classList.add('ring-2', 'ring-emerald-400', 'border-emerald-400');
            document.querySelector('[name="hosting_options"]').value = card.dataset.value;
        });
    });
}

// Step 9: Access Model
function initializeAccessModel() {
    document.querySelectorAll('.access-model-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.access-model-btn').forEach(b => {
                b.classList.remove('bg-emerald-500/10', 'border-emerald-400', 'text-emerald-300');
            });
            btn.classList.add('bg-emerald-500/10', 'border-emerald-400', 'text-emerald-300');
            document.querySelector('[name="access_model"]').value = btn.dataset.value;
        });
    });
}

// Step 9: Integrations
function initializeIntegrations() {
    const input = document.getElementById('integration-input');
    const container = document.getElementById('integrations-container');
    
    if (input && container) {
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && input.value.trim()) {
                e.preventDefault();
                const tool = input.value.trim();
                const pill = document.createElement('span');
                pill.className = 'inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-400/50 text-emerald-300 text-sm';
                pill.innerHTML = `${tool} <button type="button" class="remove-integration ml-1 hover:text-emerald-100"><i class="fas fa-times"></i></button>`;
                
                pill.querySelector('.remove-integration').addEventListener('click', () => {
                    pill.remove();
                });
                
                container.appendChild(pill);
                input.value = '';
            }
        });
    }
}

// Step 9: Analytics
function initializeAnalytics() {
    const checkbox = document.getElementById('analytics-reports');
    const frequency = document.getElementById('analytics-frequency');
    
    if (checkbox && frequency) {
        checkbox.addEventListener('change', () => {
            if (checkbox.checked) {
                frequency.classList.remove('hidden');
            } else {
                frequency.classList.add('hidden');
            }
        });
        
        document.querySelectorAll('.frequency-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.frequency-btn').forEach(b => {
                    b.classList.remove('bg-emerald-500/10', 'border-emerald-400', 'text-emerald-300');
                });
                btn.classList.add('bg-emerald-500/10', 'border-emerald-400', 'text-emerald-300');
                document.querySelector('[name="analytics_frequency"]').value = btn.dataset.value;
            });
        });
    }
}

// Step 10: Priorities
function initializePriorities() {
    let priorityOrder = [];
    const maxPriorities = 3;
    
    document.querySelectorAll('.priority-card').forEach(card => {
        card.addEventListener('click', () => {
            const value = card.dataset.value;
            const index = priorityOrder.indexOf(value);
            
            if (index > -1) {
                // Remove priority
                priorityOrder.splice(index, 1);
                card.classList.remove('ring-2', 'ring-emerald-400', 'border-emerald-400');
                card.querySelector('h3').textContent = card.querySelector('h3').textContent.replace(/^#\d+ /, '');
            } else if (priorityOrder.length < maxPriorities) {
                // Add priority
                priorityOrder.push(value);
                const priorityNum = priorityOrder.length;
                card.classList.add('ring-2', 'ring-emerald-400', 'border-emerald-400');
                const title = card.querySelector('h3');
                title.textContent = `#${priorityNum} ${title.textContent.replace(/^#\d+ /, '')}`;
            }
            
            document.querySelector('[name="priorities"]').value = priorityOrder.join(',');
        });
    });
}

// Step 11: Decision Makers
function initializeDecisionMakers() {
    const addBtn = document.getElementById('add-decision-maker');
    if (addBtn) {
        addBtn.addEventListener('click', () => {
            const list = document.getElementById('decision-makers-list');
            const template = list.querySelector('.decision-maker-item').cloneNode(true);
            template.querySelectorAll('input').forEach(input => input.value = '');
            list.appendChild(template);
        });
    }
}

// Step 11: Feedback Speed
function initializeFeedbackSpeed() {
    document.querySelectorAll('.feedback-speed-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.feedback-speed-btn').forEach(b => {
                b.classList.remove('bg-emerald-500/10', 'border-emerald-400', 'text-emerald-300');
            });
            btn.classList.add('bg-emerald-500/10', 'border-emerald-400', 'text-emerald-300');
            document.querySelector('[name="feedback_speed"]').value = btn.dataset.value;
        });
    });
}

// Modal
function initializeModal() {
    const closeBtn = document.getElementById('close-modal');
    const modal = document.getElementById('success-modal');
    
    if (closeBtn && modal) {
        closeBtn.addEventListener('click', () => {
            modal.classList.add('hidden');
        });
        
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.add('hidden');
            }
        });
    }
}

// Form Submission
function submitForm() {
    if (validateStep(currentStep)) {
        // Collect all form data
        const formData = collectFormData();
        
        // Save to state
        Object.assign(state, formData);
        saveState();
        
        // Show success modal
        document.getElementById('success-modal').classList.remove('hidden');
        
        // In production, you would send this to your backend:
        // fetch('/api/submit-course-blueprint', {
        //     method: 'POST',
        //     headers: { 'Content-Type': 'application/json' },
        //     body: JSON.stringify(formData)
        // });
        
        console.log('Form Data:', formData);
    }
}

function collectFormData() {
    const data = {};
    
    // Collect all inputs
    document.querySelectorAll('input, textarea, select').forEach(field => {
        if (field.name && field.type !== 'button' && field.type !== 'submit') {
            if (field.type === 'checkbox') {
                data[field.name] = field.checked;
            } else if (field.type === 'radio') {
                if (field.checked) {
                    data[field.name] = field.value;
                }
            } else if (field.name.endsWith('[]')) {
                // Handle array fields
                const key = field.name.replace('[]', '');
                if (!data[key]) data[key] = [];
                if (field.value) data[key].push(field.value);
            } else {
                if (field.value) data[field.name] = field.value;
            }
        }
    });
    
    // Collect tags/pills
    const skills = Array.from(document.querySelectorAll('#skills-container span')).map(span => {
        return span.textContent.replace('×', '').trim();
    });
    if (skills.length) data.skills = skills;
    
    const integrations = Array.from(document.querySelectorAll('#integrations-container span')).map(span => {
        return span.textContent.replace('×', '').trim();
    });
    if (integrations.length) data.integrations = integrations;
    
    return data;
}

// LocalStorage
function saveState() {
    const formData = collectFormData();
    formData.currentStep = currentStep;
    localStorage.setItem('courseOnboardingState', JSON.stringify(formData));
}

function loadState() {
    const saved = localStorage.getItem('courseOnboardingState');
    if (saved) {
        const data = JSON.parse(saved);
        currentStep = data.currentStep || 1;
        
        // Restore form values
        Object.keys(data).forEach(key => {
            if (key === 'currentStep') return;
            
            const field = document.querySelector(`[name="${key}"]`);
            if (field) {
                if (field.type === 'checkbox') {
                    field.checked = data[key];
                } else if (field.type === 'radio') {
                    const radio = document.querySelector(`[name="${key}"][value="${data[key]}"]`);
                    if (radio) radio.checked = true;
                } else {
                    field.value = data[key];
                }
            }
        });
        
        // Restore UI states (pills, cards, etc.)
        restoreUIStates(data);
    }
}

function restoreUIStates(data) {
    // This would restore the visual state of pills, cards, etc.
    // For now, we'll just restore the basic form values
    // In a full implementation, you'd restore all the visual states too
}

