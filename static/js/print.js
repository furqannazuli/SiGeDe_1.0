// print.js - Printing functionality for SiGeDe EMR system

document.addEventListener('DOMContentLoaded', function() {
    // Print Patient ID Band
    const printBandBtn = document.getElementById('print-id-band');
    if (printBandBtn) {
        printBandBtn.addEventListener('click', function() {
            const printContents = document.getElementById('printable-id-band').innerHTML;
            const originalContents = document.body.innerHTML;
            
            // Create a new window with only the band content
            document.body.innerHTML = `
                <html>
                <head>
                    <title>Patient ID Band</title>
                    <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
                    <link href="/static/css/custom.css" rel="stylesheet">
                    <style>
                        body {
                            background-color: white;
                            color: black;
                            padding: 0;
                            margin: 0;
                        }
                        @media print {
                            @page {
                                size: 3in 1in;
                                margin: 0;
                            }
                        }
                    </style>
                </head>
                <body>
                    ${printContents}
                </body>
                </html>
            `;
            
            window.print();
            
            // Restore original contents
            document.body.innerHTML = originalContents;
            
            // Reattach event listeners
            document.addEventListener('DOMContentLoaded', function() {
                const newPrintBtn = document.getElementById('print-id-band');
                if (newPrintBtn) {
                    newPrintBtn.addEventListener('click', function() {
                        window.location.reload(); // Reload to ensure proper re-initialization
                    });
                }
            });
        });
    }
    
    // Print Assessment Form
    const printAssessmentBtn = document.getElementById('print-assessment');
    if (printAssessmentBtn) {
        printAssessmentBtn.addEventListener('click', function() {
            const printContents = document.getElementById('printable-assessment').innerHTML;
            const originalContents = document.body.innerHTML;
            
            // Create a new window with only the assessment content
            document.body.innerHTML = `
                <html>
                <head>
                    <title>Patient Assessment</title>
                    <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
                    <link href="/static/css/custom.css" rel="stylesheet">
                    <style>
                        body {
                            background-color: white;
                            color: black;
                            padding: 20px;
                        }
                        .form-section {
                            background-color: white;
                            border: 1px solid #ddd;
                        }
                        .section-title {
                            border-bottom: 1px solid #ddd;
                        }
                        @media print {
                            .no-print {
                                display: none !important;
                            }
                        }
                    </style>
                </head>
                <body>
                    <div class="container">
                        ${printContents}
                    </div>
                </body>
                </html>
            `;
            
            window.print();
            
            // Restore original contents
            document.body.innerHTML = originalContents;
            
            // Reattach event listeners
            document.addEventListener('DOMContentLoaded', function() {
                const newPrintBtn = document.getElementById('print-assessment');
                if (newPrintBtn) {
                    newPrintBtn.addEventListener('click', function() {
                        window.location.reload(); // Reload to ensure proper re-initialization
                    });
                }
            });
        });
    }
    
    // Print Discharge Instructions
    const printDischargeBtn = document.getElementById('print-discharge');
    if (printDischargeBtn) {
        printDischargeBtn.addEventListener('click', function() {
            const printContents = document.getElementById('printable-discharge').innerHTML;
            const originalContents = document.body.innerHTML;
            
            // Create a new window with only the discharge content
            document.body.innerHTML = `
                <html>
                <head>
                    <title>Discharge Instructions</title>
                    <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
                    <link href="/static/css/custom.css" rel="stylesheet">
                    <style>
                        body {
                            background-color: white;
                            color: black;
                            padding: 20px;
                        }
                        .form-section {
                            background-color: white;
                            border: 1px solid #ddd;
                        }
                        .section-title {
                            border-bottom: 1px solid #ddd;
                        }
                        @media print {
                            .no-print {
                                display: none !important;
                            }
                        }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1 class="text-center mb-4">Discharge Instructions</h1>
                        ${printContents}
                    </div>
                </body>
                </html>
            `;
            
            window.print();
            
            // Restore original contents
            document.body.innerHTML = originalContents;
            
            // Reattach event listeners
            document.addEventListener('DOMContentLoaded', function() {
                const newPrintBtn = document.getElementById('print-discharge');
                if (newPrintBtn) {
                    newPrintBtn.addEventListener('click', function() {
                        window.location.reload(); // Reload to ensure proper re-initialization
                    });
                }
            });
        });
    }
});
