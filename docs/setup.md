# Environment Setup

Follow these steps to set up the local development environment for the **Totvs Sync Agent**.

## Prerequisites
- **Python 3.12** or higher.
- **Git**.

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd controle_estoque
   ```

2. **Set up Virtual Environment**:
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install playwright openpyxl pandas python-dotenv
   playwright install chromium
   ```

4. **Environment Variables**:
   Create a `.env` file in the root directory based on the project requirements:
   ```env
   TOTVS_USER=your_user
   TOTVS_PASSWORD=your_password
   TOTVS_URL=https://...
   ```
