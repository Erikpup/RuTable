document.addEventListener('DOMContentLoaded', function() {
    const table = document.getElementById('myTable');
    const modalManager = new Modal(generateTable);
    generateTable();
    document.querySelector('.clickable-image').addEventListener('click', handleAddClick);
    document.querySelector('.addColumnBtn').addEventListener('click', handleAddColumnClick);

    function handleAddClick() {
//        const table = document.getElementById('myTable');
//        const tbody = table.querySelector('tbody');
//        const thead = table.querySelector('thead');
//
//        // Проверяем, есть ли заголовок в таблице
//        if (!thead || thead.rows.length === 0) {
//            console.error("Заголовок таблицы не найден!");
//            return;
//        }
//
//        // Получаем количество столбцов из первого ряда заголовка
//        const numCols = thead.rows[0].cells.length - 1;  // Минус 1, так как первый столбец - это номер строки
//        const numRows = tbody.rows.length; // Количество строк
//        // Добавляем строку
//        const row = tbody.insertRow(); // Добавляем новую строку
//        row.insertCell().textContent = numRows + 1; // Добавляем номер строки
//
//        // Добавляем ячейки ко всем столбцам (кроме первого столбца с номером строки)
//        for (let j = 0; j < numCols; j++) {
//            const cell = row.insertCell(); // Создаём ячейку для каждого столбца
//            const input = document.createElement('input'); // Создаём input
//            input.type = 'text'; // Тип input
//            input.value = ''; // Оставляем значение пустым
//            input.title = toRussianCol(j + 1) + (numRows + 1); // Назначаем title ячейке, например "А2", "Б2"
//            cell.appendChild(input); // Вставляем input в ячейку
//            cell.title = toRussianCol(j + 1) + (numRows + 1); // Назначаем title ячейке для отображения
//        }
        fetch(`/add_new_row/`)
        .then(response => {
            if (!response.ok) {
                throw new Error("Ошибка сервера при генерации таблицы.");
            }
            return response.json();
        })
        .then(data => {generateTable();})


    }

    function handleAddColumnClick() {
//        const table = document.getElementById('myTable');
//        const tbody = table.querySelector('tbody');
//        const thead = table.querySelector('thead');
//
//        if (!thead || thead.rows.length === 0) {
//            console.error("Заголовок таблицы не найден!");
//            return;
//        }
//
//        const numRows = tbody.rows.length;
//        const numCols = thead.rows[0].cells.length;
//
//        const headerRow = thead.rows[0];
//        const newHeaderCell = document.createElement('th');
//        newHeaderCell.textContent = toRussianCol(numCols + 1);
//        headerRow.appendChild(newHeaderCell);
//
//        for (let i = 0; i < numRows; i++) {
//            const row = tbody.rows[i];
//            const newCell = row.insertCell();
//            const input = document.createElement('input');
//            input.type = 'text';
//            input.value = '';
//            input.title = toRussianCol(numCols + 1) + (i + 1);
//            newCell.appendChild(input);
//            newCell.title = toRussianCol(numCols + 1) + (i + 1);
//        }
        fetch(`/add_new_col/`)
        .then(response => {
            if (!response.ok) {
                throw new Error("Ошибка сервера при генерации таблицы.");
            }
            return response.json();
        })
        .then(data => {generateTable();})
    }

    function generateTable() {

        try {
            fetch(`/generate_table/`)
            .then(response => {
                if (!response.ok) {
                    throw new Error("Ошибка сервера при генерации таблицы.");
                }
                return response.json();
            })
            .then(data => {
                const tableData = data.table;
                const numCols = data.cols;
                const numRows = data.rows;
                if (numCols <= 0 || numRows <= 0) {
                    throw new Error("Количество строк и столбцов должно быть больше 0.");
                }
                const thead = table.querySelector('thead');
                const tbody = table.querySelector('tbody');

                thead.innerHTML = '';
                tbody.innerHTML = '';

                const headerRow = thead.insertRow();
                headerRow.insertCell().textContent = '№';

                for (let i = 0; i < numCols; i++) {
                    headerRow.insertCell().textContent = toRussianCol(i + 1);
                }

                for (let i = 0; i < numRows; i++) {
                    const row = tbody.insertRow();
                    row.insertCell().textContent = i + 1;
                    for (let j = 0; j < numCols; j++) {
                        const cell = row.insertCell();
                        const input = document.createElement('input');
                        input.value = tableData[i][j];
                        input.type = 'text';
                        input.title = toRussianCol(j + 1) + (i + 1);
                        cell.appendChild(input);

                        // Добавляем адрес ячейки в виде "А1", "Б2", и т.д.
                        cell.title = toRussianCol(j + 1) + (i + 1);
                    }
                }
            });
        } catch (error) {
            alert(error.message);
            console.error(error);
        }
    }

    function toRussianCol(n) {
        const russianAlphabet = ['А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ё', 'Ж', 'З', 'И', 'Й', 'К', 'Л', 'М', 'Н', 'О', 'П', 'Р', 'С', 'Т', 'У', 'Ф', 'Х', 'Ц', 'Ч', 'Ш', 'Щ', 'Э', 'Ю', 'Я','+'];
        let result = '';
        let index = n - 1;

        while (index >= 0) {
            result = russianAlphabet[index % russianAlphabet.length] + result;
            index = Math.floor(index / russianAlphabet.length) - 1;
        }

        return result;
    }

    table.addEventListener('focusin', function(event) {
        if (event.target.tagName === 'INPUT' && !modalManager.modalOpen) {
            fetch(`/get_cell/?text=${event.target.title}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error("Ошибка сервера при получении ячейки.");
                }
                return response.json();
            })
            .then(data => {
                const totalValue = data.total_value;
                event.target.value = totalValue;
                if (totalValue.startsWith('=')) { // Проверка на формулу
                    modalManager.create(event.target);
                    modalManager.disableInputs();
                } else {
                    modalManager.create(event.target);
                    modalManager.disableInputs();
                }
            });

        }
        else if (event.target.tagName === 'INPUT'){
            modalManager.textarea.value = modalManager.textarea.value + event.target.title;
        }
    });
});

class Modal {
    constructor(generateTable) {
        this.modal = null;
        this.modalOpen = false;
        this.isDragging = false;
        this.offsetX = 0;
        this.offsetY = 0;
        this.inputElement = null;
        this.predefinedText = '';
        this.generateTable = generateTable; // Сохраняем функцию generateTable

        this.initEventListeners();
    }

    create(inputElement) {
        this.inputElement = inputElement;

        // модальное окно
        this.modal = document.createElement('div');
        this.modal.id = 'myModal';

        // Контейнер для содержимого модального окна
        const modalContent = document.createElement('div');

        // Текстовое поле
        this.textarea = document.createElement('textarea');
        const address = inputElement.title;
        this.textarea.value = inputElement.value; // Значение ячейки в поле ввода
        this.textarea.addEventListener('input', () => {
            fetch('/check_cell/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json', // Указываем, что данные отправляются в формате JSON
                },
                body: JSON.stringify({ text: this.textarea.value }), // Отправляем JSON с адресом и значением
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error("Ошибка сервера при получении ячейки.");
                }
                return response.json();
            })
            .then(data => {
                    const totalValue = data.text;
                    outputDiv.textContent = totalValue;
                });
        });

        // Контейнер для кнопок
        const buttonContainer = document.createElement('div');

        // Кнопка отправки
        const sendButton = document.createElement('button');
        sendButton.textContent = 'Отправить';

        sendButton.addEventListener('click', () => this.close(this.textarea,address));

        // "Enter"
        this.textarea.addEventListener('keydown', (event) => {
            if (event.key === 'Enter') {
                this.close(this.textarea,address);
            }
        });

        // Элемент для вывода текста
        const outputDiv = document.createElement('div');

        fetch('/check_cell/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json', // Указываем, что данные отправляются в формате JSON
            },
            body: JSON.stringify({ text: this.textarea.value }), // Отправляем JSON с адресом и значением
        })
        .then(response => {
            if (!response.ok) {
                throw new Error("Ошибка сервера при получении ячейки.");
            }
            return response.json();
        })
        .then(data => {
                const totalValue = data.text;
                outputDiv.textContent = totalValue;
            });
//        outputDiv.textContent = this.predefinedText;
        outputDiv.style.marginTop = '10px';

        // элементы в модальном окне
        buttonContainer.appendChild(sendButton);
        modalContent.appendChild(this.textarea);
        modalContent.appendChild(outputDiv);
        modalContent.appendChild(buttonContainer);
        this.modal.appendChild(modalContent);

        this.modal.addEventListener('mousedown', (e) => {
            if (e.target === this.modal) {
                this.isDragging = true;
                this.offsetX = e.clientX - this.modal.offsetLeft;
                this.offsetY = e.clientY - this.modal.offsetTop;
            }
        });

        document.body.appendChild(this.modal);
        this.textarea.focus();
        this.modalOpen = true;

        // Активная ячейка
        this.inputElement.style.border = '2px solid #c6f68b';
    }

    close(textarea, address) {
        fetch('/save_cell/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json', // Указываем, что данные отправляются в формате JSON
            },
            body: JSON.stringify({ address: address, text: textarea.value }), // Отправляем JSON с адресом и значением
        })
        .then(response => {
            if (!response.ok) {
                throw new Error("Ошибка сервера при получении ячейки.");
            }
            return response.json();
        })
        .then(data => {
                const totalValue = data.text;
                this.modalOpen = false;
                this.inputElement.value = totalValue;
                document.body.removeChild(this.modal);
                this.enableInputs();
                // Убираем выделение с активной ячейки
                this.inputElement.style.border = '';
                this.generateTable();
            });

    }
    initEventListeners() {
        document.addEventListener('mousemove', (e) => {
            if (this.isDragging) {
                this.modal.style.left = (e.clientX - this.offsetX) + 'px';
                this.modal.style.top = (e.clientY - this.offsetY) + 'px';
            }
        });

        document.addEventListener('mouseup', () => {
            this.isDragging = false;
        });
    }

    enableInputs() {
        const inputs = document.querySelectorAll('#myTable input');
        inputs.forEach(input => input.disabled = false);
    }

    disableInputs() {
        const inputs = document.querySelectorAll('#myTable input');
        inputs.forEach(input => {
            if (input !== this.inputElement) {
                input.disabled = true;
            }
        });
    }
}