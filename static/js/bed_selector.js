document.addEventListener('DOMContentLoaded', function() {
    // Only initialize on inpatient transfer page
    if (document.getElementById('bed-selection-container')) {
        initBedSelector();
    }
});

function initBedSelector() {
    const wardSelect = document.getElementById('destination_ward');
    const bedSelector = document.getElementById('bed-selection-container');
    const bedNumberInput = document.getElementById('bed_number');
    const bedAvailableRadios = document.querySelectorAll('input[name="is_bed_available"]');
    const waitingListFields = document.getElementById('waiting-list-fields');
    
    // Mock data for beds - in a real implementation, this would come from an API
    const wardsData = {
        'General Medicine': generateWardData('GM', 20, 16),
        'Cardiology': generateWardData('CARD', 16, 10),
        'Neurology': generateWardData('NEURO', 12, 8),
        'Orthopedics': generateWardData('ORTHO', 15, 9),
        'Surgery': generateWardData('SURG', 18, 12),
        'Pediatrics': generateWardData('PEDS', 24, 18),
        'Intensive Care': generateWardData('ICU', 8, 7),
        'Coronary Care': generateWardData('CCU', 6, 4),
        'Obstetrics': generateWardData('OB', 10, 6),
        'Gynecology': generateWardData('GYN', 8, 5),
        'Oncology': generateWardData('ONC', 12, 9),
        'Pulmonology': generateWardData('PULM', 10, 7),
        'Nephrology': generateWardData('NEPH', 8, 5),
        'Gastroenterology': generateWardData('GASTRO', 10, 8),
        'Neonatal ICU': generateWardData('NICU', 12, 10),
        'Psychiatric': generateWardData('PSYCH', 20, 15),
        'Rehabilitation': generateWardData('REHAB', 16, 12)
    };
    
    let selectedBed = null;
    
    // Event listeners
    wardSelect.addEventListener('change', function() {
        updateBedDisplay(this.value);
        
        // Check if there are any available beds in this ward
        const wardData = wardsData[this.value];
        const availableBeds = wardData.beds.filter(bed => !bed.occupied);
        
        // Auto-select Yes/No for bed availability based on available beds
        if (availableBeds.length > 0) {
            document.getElementById('bed_available_yes').checked = true;
            waitingListFields.classList.add('d-none');
        } else {
            document.getElementById('bed_available_no').checked = true;
            waitingListFields.classList.remove('d-none');
        }
    });
    
    // Toggle waiting list fields based on bed availability selection
    bedAvailableRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.value === 'yes') {
                waitingListFields.classList.add('d-none');
            } else {
                waitingListFields.classList.remove('d-none');
            }
        });
    });
    
    // Initial bed display if a ward is already selected
    if (wardSelect.value) {
        updateBedDisplay(wardSelect.value);
    }
    
    function updateBedDisplay(wardName) {
        const wardData = wardsData[wardName];
        if (!wardData) return;
        
        // Clear previous selection
        selectedBed = null;
        bedNumberInput.value = '';
        
        // Create the bed visualization
        bedSelector.innerHTML = `
            <div class="bed-selection-header mt-3 mb-3">
                <h5>${wardName} Ward - ${wardData.beds.length} Beds</h5>
                <div class="bed-legend">
                    <span class="bed-legend-item"><span class="bed-icon available"></span> Available</span>
                    <span class="bed-legend-item"><span class="bed-icon occupied"></span> Occupied</span>
                    <span class="bed-legend-item"><span class="bed-icon selected"></span> Selected</span>
                </div>
            </div>
            <div class="row ward-layout">
                <div class="col-md-8 bed-grid" id="bed-grid"></div>
                <div class="col-md-4">
                    <div class="ward-info card">
                        <div class="card-body">
                            <h6 class="card-title">Ward Information</h6>
                            <p><strong>Total Beds:</strong> ${wardData.beds.length}</p>
                            <p><strong>Occupied Beds:</strong> ${wardData.beds.filter(b => b.occupied).length}</p>
                            <p><strong>Available Beds:</strong> ${wardData.beds.filter(b => !b.occupied).length}</p>
                            <div class="selected-bed-info mt-3">
                                <h6>Selected Bed</h6>
                                <p id="selected-bed-display">None selected</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        const bedGrid = document.getElementById('bed-grid');
        const rows = Math.ceil(wardData.beds.length / 4); // 4 beds per row
        
        // Create the bed grid
        for (let row = 0; row < rows; row++) {
            const rowDiv = document.createElement('div');
            rowDiv.className = 'bed-row';
            
            for (let col = 0; col < 4; col++) {
                const bedIndex = row * 4 + col;
                if (bedIndex < wardData.beds.length) {
                    const bed = wardData.beds[bedIndex];
                    const bedDiv = document.createElement('div');
                    bedDiv.className = `bed-cell ${bed.occupied ? 'occupied' : 'available'}`;
                    bedDiv.setAttribute('data-bed-id', bed.id);
                    bedDiv.innerHTML = `
                        <div class="bed-icon"></div>
                        <div class="bed-label">${bed.id}</div>
                    `;
                    
                    // Only allow selection of available beds
                    if (!bed.occupied) {
                        bedDiv.addEventListener('click', function() {
                            selectBed(bed.id, bedDiv);
                        });
                    }
                    
                    rowDiv.appendChild(bedDiv);
                }
            }
            
            bedGrid.appendChild(rowDiv);
        }
    }
    
    function selectBed(bedId, bedElement) {
        // Clear previous selection
        const previousSelection = document.querySelector('.bed-cell.selected');
        if (previousSelection) {
            previousSelection.classList.remove('selected');
        }
        
        // Update selection
        selectedBed = bedId;
        bedElement.classList.add('selected');
        
        // Update form field
        bedNumberInput.value = bedId;
        
        // Update display
        document.getElementById('selected-bed-display').textContent = bedId;
        
        // Ensure "Yes" is selected for bed availability
        document.getElementById('bed_available_yes').checked = true;
        waitingListFields.classList.add('d-none');
    }
}

// Helper function to generate mock data for a ward
function generateWardData(prefix, totalBeds, occupiedCount) {
    const beds = [];
    const occupiedBeds = new Set();
    
    // Generate a set of random occupied beds
    while (occupiedBeds.size < occupiedCount) {
        occupiedBeds.add(Math.floor(Math.random() * totalBeds) + 1);
    }
    
    // Create the bed objects
    for (let i = 1; i <= totalBeds; i++) {
        beds.push({
            id: `${prefix}-${i.toString().padStart(2, '0')}`,
            occupied: occupiedBeds.has(i)
        });
    }
    
    return { beds };
}