// main.js - Main JavaScript for SiGeDe EMR system

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Handle arrival mode selection in patient registration
    const arrivalModeRadios = document.querySelectorAll('input[name="arrival_mode"]');
    const ambulanceFields = document.getElementById('ambulance-fields');
    const walkInFields = document.getElementById('walk-in-fields');

    if (arrivalModeRadios.length > 0) {
        arrivalModeRadios.forEach(function(radio) {
            radio.addEventListener('change', function() {
                if (this.value === 'ambulance') {
                    if (ambulanceFields) ambulanceFields.classList.remove('d-none');
                    if (walkInFields) walkInFields.classList.add('d-none');
                } else if (this.value === 'walk-in') {
                    if (ambulanceFields) ambulanceFields.classList.add('d-none');
                    if (walkInFields) walkInFields.classList.remove('d-none');
                }
            });
        });
    }

    // Generate MRN button functionality
    const generateMrnBtn = document.getElementById('generate-mrn-btn');
    if (generateMrnBtn) {
        generateMrnBtn.addEventListener('click', function() {
            fetch('/admin/generate-mrn', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('medical_record_number').value = data.mrn;
            })
            .catch(error => {
                console.error('Error generating MRN:', error);
            });
        });
    }

    // Triage category selection highlighting
    const triageCategoryRadios = document.querySelectorAll('input[name="triage_category"]');
    const triageDisplay = document.getElementById('triage-display');
    
    if (triageCategoryRadios.length > 0) {
        triageCategoryRadios.forEach(function(radio) {
            radio.addEventListener('change', function() {
                if (triageDisplay) {
                    // Remove all existing triage classes
                    triageDisplay.classList.remove('triage-red', 'triage-yellow', 'triage-green', 'triage-black');
                    // Add the selected class
                    triageDisplay.classList.add('triage-' + this.value);
                    triageDisplay.textContent = this.value.toUpperCase() + ' Triage';
                }
            });
        });
    }

    // Auto-save functionality for forms
    let autoSaveTimer;
    const autoSaveDelay = 5000; // 5 seconds
    const formWithAutoSave = document.querySelector('form[data-autosave="true"]');
    const autoSaveIndicator = document.querySelector('.autosave-indicator');
    
    if (formWithAutoSave && autoSaveIndicator) {
        const formInputs = formWithAutoSave.querySelectorAll('input, textarea, select');
        
        formInputs.forEach(input => {
            input.addEventListener('input', function() {
                // Clear any existing timer
                clearTimeout(autoSaveTimer);
                
                // Show saving indicator
                autoSaveIndicator.textContent = 'Saving...';
                autoSaveIndicator.classList.add('saving');
                autoSaveIndicator.classList.remove('saved');
                
                // Set new timer
                autoSaveTimer = setTimeout(function() {
                    // Here you would normally send an AJAX request to save the form data
                    // For demo, just simulate a successful save
                    setTimeout(function() {
                        autoSaveIndicator.textContent = 'Saved';
                        autoSaveIndicator.classList.remove('saving');
                        autoSaveIndicator.classList.add('saved');
                        
                        // Hide the saved message after a few seconds
                        setTimeout(function() {
                            autoSaveIndicator.classList.remove('saved');
                        }, 3000);
                    }, 1000);
                }, autoSaveDelay);
            });
        });
    }

    // Add required validation to lab/radiology test fields when requested
    const requiresLabTestsCheckbox = document.getElementById('requires_lab_tests');
    const labTestsSection = document.getElementById('lab-tests-section');
    
    if (requiresLabTestsCheckbox && labTestsSection) {
        requiresLabTestsCheckbox.addEventListener('change', function() {
            if (this.checked) {
                labTestsSection.classList.remove('d-none');
            } else {
                labTestsSection.classList.add('d-none');
            }
        });
    }

    // Disposition type selection logic
    const dispositionTypeRadios = document.querySelectorAll('input[name="disposition_type"]');
    const dispositionSections = {
        'discharge': document.getElementById('discharge-fields'),
        'outpatient': document.getElementById('outpatient-fields'),
        'inpatient': document.getElementById('inpatient-fields'),
        'deceased': document.getElementById('deceased-fields')
    };
    
    if (dispositionTypeRadios.length > 0) {
        dispositionTypeRadios.forEach(function(radio) {
            radio.addEventListener('change', function() {
                const selectedType = this.value;
                
                // Hide all sections first
                Object.values(dispositionSections).forEach(section => {
                    if (section) section.classList.add('d-none');
                });
                
                // Show the selected section
                if (dispositionSections[selectedType]) {
                    dispositionSections[selectedType].classList.remove('d-none');
                }
            });
        });
    }

    // Bed availability toggle for inpatient transfer
    const bedAvailabilityRadios = document.querySelectorAll('input[name="is_bed_available"]');
    const waitingListFields = document.getElementById('waiting-list-fields');
    
    if (bedAvailabilityRadios.length > 0 && waitingListFields) {
        bedAvailabilityRadios.forEach(function(radio) {
            radio.addEventListener('change', function() {
                if (this.value === 'no') {
                    waitingListFields.classList.remove('d-none');
                } else {
                    waitingListFields.classList.add('d-none');
                }
            });
        });
    }
});
