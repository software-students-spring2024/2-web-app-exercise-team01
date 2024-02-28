document.addEventListener('DOMContentLoaded', () => {
    const navList = document.getElementById('navList');
    const content = document.getElementById('content');
    // Initialize the page with the 'upload' content
    loadContent('upload');

    const uploadButton = document.getElementById('uploadDataButton');

    uploadButton.addEventListener('click', function() {
        document.getElementById('uploadInput').click();
    });

    navList.addEventListener('click', (event) => {
        let target = event.target;
        if (target.tagName.toLowerCase() === 'li') {
            const targetId = target.getAttribute('data-target');
            setActiveTab(targetId);
            loadContent(targetId);
        }
    });

    function setActiveTab(targetId) {
        document.querySelectorAll('#navList li').forEach(li => {
            li.classList.remove('active');
        });
        document.querySelector(`#navList li[data-target="${targetId}"]`).classList.add('active');
    }

    function loadContent(targetId) {
        // Define content for each tab
        const tabContent = {
            'upload': `
                <header>
                    <h2>Upload</h2>
                    <button id="uploadDataButton">Upload Data</button>
                    <input type="file" id="uploadInput" accept=".csv" style="display: none"
                        onchange="document.getElementById('uploadSection').innerHTML = 'File uploaded: ' + this.files[0].name"
                    />
                    <div id="profilePicture"></div>
                </header>
                <div id="uploadSection">
                    <p>Click here to upload a CSV of your trades (opens finder)</p>
                </div>
            `,
            'dashboard': `
                <header>
                    <h2>Dashboard</h2>
                    <button id="uploadDataButton">Upload Data</button>
                    <div id="profilePicture"></div>
                </header>
                <div id="dashboardSection">
                    <div id="profitLoss">
                        <h3>P/L: $1000</h3>
                        <p>+ $30 (3.09%)</p>
                    </div>
                    <div id="graphContainer">
                        <p>Graph image placeholder</p>
                        <!-- Placeholder for graph image. Replace with actual image or graph drawing logic -->
                    </div>
                    <div id="timeFilters">
                        <span>1D</span>
                        <span>1W</span>
                        <span>1M</span>
                        <span>3M</span>
                        <span>YTD</span>
                        <span>1Y</span>
                        <span>ALL</span>
                    </div>
                    <div class="infoSection">
                        <h4>Current Positions &gt;</h4>
                        <div class="infoContent">
                            <p>Portfolio details placeholder</p>
                            <!-- Placeholder for portfolio details. Replace with actual content -->
                        </div>
                    </div>
                    <div class="infoSection">
                        <h4>Orders &gt;</h4>
                        <div class="infoContent">
                            <p>Order details placeholder</p>
                            <!-- Placeholder for order details. Replace with actual content -->
                        </div>
                    </div>
                </div>
            `,
            'taxes': `
            <header>
            <h2>Taxes</h2>
            <button id="uploadDataButton">Upload Data</button>
            <div id="profilePicture"></div>
        </header>
        <div id="taxesSection">
            <div id="profitLoss">
                <h3>P/L: $1000</h3>
                <p>+ $30 (3.09%)</p>
            </div>
            <div id="graphContainer">
                <p>graph image</p>
            </div>
            <div id="timeFilters">
                <span>1D</span>
                <span>1W</span>
                <span>1M</span>
                <span>3M</span>
                <span>YTD</span>
                <span>1Y</span>
                <span>ALL</span>
            </div>
            <div class="infoSection">
                <h4>P&L By Token</h4>
                <div class="infoContent">
                    <p>Portfolio details</p>
                </div>
            </div>
            <div class="infoSection">
                <h4>Cost basis per token</h4>
                <div class="infoContent">
                    <p>Token details</p>
                </div>
            </div>
            <div class="infoSection">
                <h4>Proceeds per token</h4>
                <div class="infoContent">
                    <p>Token details</p>
                </div>
            </div>
        </div>            `,
            'insights': `
            <header>
            <h2>Insights</h2>
            <button id="uploadDataButton">Upload Data</button>
            <div id="profilePicture"></div>
        </header>
        <div id="insightsSection">
            <div class="infoSection">
                <h4>P&L By Token</h4>
                <div class="infoContent">
                    <p>Trade details</p>
                </div>
            </div>
            <div class="infoSection">
                <h4>P&L - Longs</h4>
                <div class="infoContent">
                    <p>Long trade details</p>
                </div>
            </div>
            <div class="infoSection">
                <h4>P&L - Shorts</h4>
                <div class="infoContent">
                    <p>Short trade details</p>
                </div>
            </div>
            <div class="infoSection">
                <h4>P&L By Holding Period</h4>
                <div class="infoContent">
                    <p>Trade details</p>
                </div>
            </div>
            <div class="infoSection full">
                <h4>More trade statistics</h4>
                <div class="infoContent">
                    <p>Trade details</p>
                </div>
            </div>
        </div>
            `
        };

        // Load the content into the 'content' section
        content.innerHTML = tabContent[targetId] || '<p>Content not found</p>';
    }
});
