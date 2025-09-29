const dropArea = document.getElementById('drop-area');
const fileInput = document.getElementById('fileElem');
const chooseBtn = document.getElementById('chooseBtn');
const sortColumnInput = document.getElementById('sort_column');
const columnsPreview = document.getElementById('columnsPreview');
const fileInfo = document.getElementById('fileInfo');

let selectedFile = null;
let fileColumns = [];

// Drag & drop события
['dragenter','dragover','dragleave','drop'].forEach(evt =>
  dropArea.addEventListener(evt, e => { e.preventDefault(); e.stopPropagation(); })
);
['dragenter','dragover'].forEach(evt =>
  dropArea.addEventListener(evt, () => dropArea.classList.add('hover')));
['dragleave','drop'].forEach(evt =>
  dropArea.addEventListener(evt, () => dropArea.classList.remove('hover')));

// Обработка drop
dropArea.addEventListener('drop', (e) => {
  const dt = e.dataTransfer;
  if(!dt.files || dt.files.length===0) return;
  fileInput.files = dt.files;
  onFileSelected();
});

// Кнопка выбора файла
chooseBtn.addEventListener('click', () => fileInput.click());

// Изменение input file
fileInput.addEventListener('change', onFileSelected);

// Файл выбран
function onFileSelected() {
  selectedFile = fileInput.files[0] || null;
  if(!selectedFile){
    fileInfo.textContent = 'Файл не выбран';
    columnsPreview.textContent = 'Колонки будут показаны здесь';
    fileColumns = [];
    return;
  }
  fileInfo.textContent = selectedFile.name;
  previewColumns(selectedFile);
}

// Предпросмотр колонок
function previewColumns(file) {
  const reader = new FileReader();
  reader.onload = function(e){
    const text = e.target.result;
    const firstLine = text.split('\n')[0];
    fileColumns = firstLine.split(',').map(c => c.trim());
    columnsPreview.innerHTML = `<b>Колонки в файле:</b> ${fileColumns.join(', ')}`;
  };
  reader.readAsText(file);
}

// Подсветка совпадений при вводе
sortColumnInput.addEventListener('input', () => {
  const val = sortColumnInput.value.trim().toLowerCase();
  if(!val){
    columnsPreview.innerHTML = `<b>Колонки в файле:</b> ${fileColumns.join(', ')}`;
    return;
  }
  const highlighted = fileColumns.map(c => 
    c.toLowerCase().startsWith(val) ? `<b>${c}</b>` : c
  );
  columnsPreview.innerHTML = `<b>Колонки в файле:</b> ${highlighted.join(', ')}`;
});
