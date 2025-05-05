# ☕ Coffee Sales Management

A Python-based CLI tool to help coffee shop owners track sales, manage inventory, and generate reports. Built for simplicity, efficiency, and extendability.

---

## 📊 Dataset Source

This project uses real-world sample data from the [Coffee Sales Dataset on Kaggle](https://www.kaggle.com/datasets/ihelon/coffee-sales).
Please download and place the dataset in the root directory as `coffee_sales.csv` or as defined in your environment variables.

---

## 🚀 Features

* 📈 Track and record coffee sales by product, quantity, and date
* 🛒 Manage inventory and prevent stockouts
* 📅 Generate daily, weekly, or monthly sales summaries
* 💾 Uses CSV for lightweight, persistent storage
* ⚙️ Easily configurable through environment variables

---

## 📁 Project Structure

```
coffee-sales-management/
├── main.py               # Main script
├── dataset.csv      # Sales dataset (download from Kaggle)
├── .env                  # Environment variables file
├── requirements.txt      # Dependencies
└── README.md             # Documentation
```

---

## 🔧 Environment Variables

Create a `.env` file in the root directory to customize configuration. Example:

```env
DB_HOST=<YOUR DB HOST>
DB_NAME=<YOUR DB NAME>
DB_USER=<YOUR DB USER>
DB_PASSWORD=<YOUR DB PASSWORD>
```


* `DB_HOST`: DB Host that is used
* `DB_NAME`: DB Name
* `DB_USER`: DB User
* `DB_PASSWORD`: DB Password

> The app will use default values if `.env` is not provided.

---

## 🧰 Installation & Usage

### 1. Clone the repository

```bash
git clone https://github.com/javoxirone/coffee-sales-management.git
cd coffee-sales-management
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set environment variables

Create a `.env` file as described above.

### 4. Run the application

```bash
python main.py
```

---

## ✅ To Do / Future Enhancements

* Add authentication system for multiple users/roles
* Export reports as PDF/Excel
* Visual charts for monthly or product-wise trends
* Web interface using Flask or Django
* Integration with SQLite or PostgreSQL

---

## 🤝 Contributing

Contributions are welcome! Please fork the repo and open a pull request with your changes.

---

## 📄 License

MIT License — see the [LICENSE](LICENSE) file for details.

---

*Developed by [javoxirone](https://github.com/javoxirone)*
