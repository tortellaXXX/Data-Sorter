const dropArea = document.getElementById('drop-area');
const fileInput = document.getElementById('fileElem');
const chooseBtn = document.getElementById('chooseBtn');
const sortColumnInput = document.getElementById('sortColumn');
const resultArea = document.getElementById('result');
const fileInfo = document.getElementById('fileInfo');
const status = document.getElementById('status');

let selectedFile = null;
let isUploading = false;

;['dragenter','dragover','dragleave','drop'].forEach(evt =>
  dropArea.addEventListener(evt, e => { e.preventDefault(); e.stopPropagation(); }, false)
);

;['dragenter','dragover'].forEach(evt =>
  dropArea.addEventListener(evt, () => dropArea.classList.add('hover'), false)
);
;['dragleave','drop'].forEach(evt =>
  dropArea.addEventListener(evt, () => dropArea.classList.remove('hover'), false)
);

// drop handler
dropArea.addEventListener('drop', handleDrop, false);
function handleDrop(e) {
  const dt = e.dataTransfer;
  if (!dt || !dt.files || dt.files.length === 0) return;
  fileInput.files = dt.files;
  onFileSelected();
}

// choose button opens file picker
chooseBtn.addEventListener('click', () => fileInput.click());

// file input change
fileInput.addEventListener('change', onFileSelected);

function onFileSelected() {
  selectedFile = fileInput.files[0] || null;
  if (!selectedFile) {
    fileInfo.textContent = 'Файл не выбран';
    return;
  }
  fileInfo.textContent = selectedFile.name;
  status.textContent = 'Файл выбран. Ожидание колонки...';
  // если колонка уже задана — сразу загружаем
  const col = sortColumnInput.value.trim();
  if (col) uploadFile(selectedFile, col);
}

// если пользователь вводит колонку и файл уже выбран — загружаем
sortColumnInput.addEventListener('input', () => {
  const col = sortColumnInput.value.trim();
  if (selectedFile && col && !isUploading) uploadFile(selectedFile, col);
});

async function uploadFile(file, sortColumn) {
  if (isUploading) return;
  isUploading = true;
  resultArea.textContent = '';
  status.textContent = 'Загрузка и обработка...';
  const fd = new FormData();
  fd.append('file', file);
  fd.append('sort_column', sortColumn);

  try {
    const res = await fetch('/sort', { method: 'POST', body: fd });
    if (!res.ok) {
      const txt = await res.text();
      status.textContent = `Ошибка сервера: ${res.status}`;
      resultArea.textContent = txt;
    } else {
      const data = await res.json();
      status.textContent = 'Готово';
      resultArea.textContent = JSON.stringify(data, null, 2);
    }
  } catch (err) {
    status.textContent = 'Ошибка сети';
    resultArea.textContent = String(err);
  } finally {
    isUploading = false;
  }
}
