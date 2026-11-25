const list = document.querySelector('#student-list');
const count = document.querySelector('#student-count');
const search = document.querySelector('#search');
const empty = document.querySelector('#empty');
const notice = document.querySelector('#notice');
const dialog = document.querySelector('#student-dialog');
const form = document.querySelector('#student-form');
const formError = document.querySelector('#form-error');
let students = [];
let editingId = null;

function showNotice(message, isError = false) {
  notice.textContent = message;
  notice.className = message ? (isError ? 'notice error' : 'notice success') : '';
}
function cell(text, className = '') {
  const td = document.createElement('td');
  td.textContent = text;
  td.className = className;
  return td;
}
function render() {
  const query = search.value.trim().toLowerCase();
  const visible = students.filter(s => [s.name, s.email, s.course, String(s.age)].some(v => v.toLowerCase().includes(query)));
  count.textContent = students.length;
  list.replaceChildren();
  for (const student of visible) {
    const row = document.createElement('tr');
    const name = cell(student.name, 'student-name');
    const initials = document.createElement('span');
    initials.className = 'avatar';
    initials.textContent = student.name.split(/\s+/).slice(0, 2).map(part => part[0]).join('').toUpperCase();
    name.prepend(initials);
    const actions = document.createElement('td');
    actions.className = 'actions';
    const edit = document.createElement('button');
    edit.className = 'text-button'; edit.textContent = 'Edit';
    edit.setAttribute('aria-label', `Edit ${student.name}`);
    edit.addEventListener('click', () => openForm(student));
    const remove = document.createElement('button');
    remove.className = 'text-button delete'; remove.textContent = 'Delete';
    remove.setAttribute('aria-label', `Delete ${student.name}`);
    remove.addEventListener('click', () => deleteStudent(student));
    actions.append(edit, remove);
    row.append(name, cell(student.email), cell(student.age), cell(student.course), actions);
    list.append(row);
  }
  empty.hidden = visible.length > 0;
  document.querySelector('#empty-text').textContent = query ? 'Try a different search term.' : 'Add your first student to get started.';
}
async function api(url, options) {
  const response = await fetch(url, options);
  const data = response.status === 204 ? null : await response.json();
  if (!response.ok) throw new Error(data?.error || 'Something went wrong. Please try again.');
  return data;
}
async function loadStudents() {
  try { students = await api('/students'); render(); }
  catch (error) { showNotice(`Could not load students: ${error.message}`, true); }
}
function openForm(student = null) {
  editingId = student ? student.id : null;
  form.reset(); formError.hidden = true;
  document.querySelector('#dialog-title').textContent = student ? 'Edit student' : 'Add student';
  document.querySelector('#save-button').textContent = student ? 'Save changes' : 'Add student';
  if (student) for (const field of ['name', 'email', 'age', 'course']) form.elements[field].value = student[field];
  dialog.showModal();
  form.elements.name.focus();
}
document.querySelector('#add-button').addEventListener('click', () => openForm());
document.querySelector('#close-dialog').addEventListener('click', () => dialog.close());
document.querySelector('#cancel-dialog').addEventListener('click', () => dialog.close());
search.addEventListener('input', render);
form.addEventListener('submit', async event => {
  event.preventDefault();
  const data = Object.fromEntries(new FormData(form));
  data.age = Number(data.age);
  const save = document.querySelector('#save-button');
  save.disabled = true; formError.hidden = true;
  try {
    const wasEditing = editingId !== null;
    await api(wasEditing ? `/students/${editingId}` : '/students', {method: wasEditing ? 'PATCH' : 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)});
    dialog.close();
    showNotice(wasEditing ? 'Student updated successfully.' : 'Student added successfully.');
    await loadStudents();
  } catch (error) { formError.textContent = error.message; formError.hidden = false; }
  finally { save.disabled = false; }
});
async function deleteStudent(student) {
  if (!window.confirm(`Delete ${student.name}? This cannot be undone.`)) return;
  try { await api(`/students/${student.id}`, {method: 'DELETE'}); showNotice('Student deleted successfully.'); await loadStudents(); }
  catch (error) { showNotice(`Could not delete student: ${error.message}`, true); }
}
loadStudents();
