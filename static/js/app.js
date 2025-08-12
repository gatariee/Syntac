let current = { name: null, sub: null };

const menu = document.getElementById('menu'),
    globalsW = document.getElementById('globals'),
    extrasW = document.getElementById('extras'),
    formG = document.getElementById('form-globals'),
    formE = document.getElementById('form-extras'),
    previewW = document.getElementById('preview'),
    previewContent = document.getElementById('preview-content'),
    searchBox = document.getElementById('search-box');

let containerPositions = {
    globals: { x: 0, y: 0 },
    extras: { x: 0, y: 0 },
    preview: { x: 0, y: 0 }
};

let zIndexCounter = 100;

interact('#globals, #extras, #preview h3').draggable({
    listeners: {
        move(event) {
            const target = event.target.parentElement.id === 'preview' ? event.target.parentElement : event.target;
            if (!target || !containerPositions.hasOwnProperty(target.id)) return;

            const x = (parseFloat(target.getAttribute('data-x')) || 0) + event.dx;
            const y = (parseFloat(target.getAttribute('data-y')) || 0) + event.dy;

            target.style.transform = `translate(${x}px, ${y}px)`;
            target.setAttribute('data-x', x);
            target.setAttribute('data-y', y);
            containerPositions[target.id] = { x, y };
        },
        start(event) {
            const target = event.target.parentElement.id === 'preview' ? event.target.parentElement : event.target;
            if (target) {
                target.style.zIndex = zIndexCounter++;
            }
        }
    }
});

// caching
function saveState() {
    const data = collect();
    for (const key in data) {
        if (key.startsWith('__')) continue;
        localStorage.setItem('field_' + key, JSON.stringify(data[key]));
    }
}

function loadState() {
    const savedState = {};
    const moduleGlobals = connectors?.[current.name]?.globals || [];
    const moduleExtras = connectors?.[current.name]?.subs?.find(s => s.key === current.sub)?.extras || [];
    const allFields = [...moduleGlobals, ...moduleExtras];
    
    allFields.forEach(field => {
        const savedValue = localStorage.getItem('field_' + field.name);
        if (savedValue !== null) {
            savedState[field.name] = JSON.parse(savedValue);
        }
    });

    return savedState;
}

function buildMenu(query = '') {
    menu.innerHTML = '';
    const lowerCaseQuery = query.toLowerCase();

    for (let name in connectors) {
        const isModuleMatch = name.toLowerCase().includes(lowerCaseQuery);
        const matchingSubs = connectors?.[name]?.subs?.filter(s => s.key.toLowerCase().includes(lowerCaseQuery)) || [];

        if (isModuleMatch || matchingSubs.length > 0) {
            const head = document.createElement('li');
            head.className = 'heading active';
            head.textContent = name;
            head.onclick = () => {
                head.classList.toggle('active');
            };
            menu.appendChild(head);

            const subList = document.createElement('ul');
            subList.className = 'sub-list';

            const subsToShow = query ? matchingSubs : connectors?.[name]?.subs || [];

            subsToShow.forEach(s => {
                const li = document.createElement('li');
                li.className = 'sub';
                li.textContent = s.key;
                li.dataset.connector = name;
                li.dataset.sub = s.key;
                li.onclick = () => selectSub(name, s.key);
                subList.appendChild(li);
            });

            menu.appendChild(subList);
        }
    }
}

searchBox.addEventListener('input', (e) => {
    buildMenu(e.target.value);
});


function selectSub(name, sub) {
    document.querySelectorAll('li.sub').forEach(e =>
        e.classList.remove('active')
    );
    const el = document.querySelector(
        `li.sub[data-connector="${name}"][data-sub="${sub}"]`
    );
    el?.classList.add('active');

    const prevConnector = current.name;
    current = { name, sub };

    localStorage.setItem('lastSelectedSub', JSON.stringify(current));

    if (name !== prevConnector) buildGlobals(name);
    buildExtras(name, sub);

    resetContainerPositions();

    updatePreview();
}

function resetContainerPositions() {
    containerPositions = {
        globals: { x: 0, y: 0 },
        extras: { x: 0, y: 0 },
        preview: { x: 0, y: 0 }
    };
    globalsW.style.transform = `translate(0px, 0px)`;
    globalsW.setAttribute('data-x', 0);
    globalsW.setAttribute('data-y', 0);

    extrasW.style.transform = `translate(0px, 0px)`;
    extrasW.setAttribute('data-x', 0);
    extrasW.setAttribute('data-y', 0);

    previewW.style.transform = `translate(0px, 0px)`;
    previewW.setAttribute('data-x', 0);
    previewW.setAttribute('data-y', 0);
}

function buildGlobals(name) {
    formG.innerHTML = '';
    const globs = connectors?.[name]?.globals || [];
    const savedState = loadState();

    if (!globs.length) {
        globalsW.style.display = 'none';
        return;
    }

    globalsW.style.display = '';
    globs.forEach(f => {
        const fieldHtml = createFieldHtml(f, savedState || {});
        formG.insertAdjacentHTML('beforeend', fieldHtml);
    });
    formG.oninput = () => {
        saveState();
        updatePreview();
    };
}

function buildExtras(name, sub) {
    formE.innerHTML = '';
    const extra = connectors?.[name]?.subs?.find(s => s.key === sub)?.extras || [];
    const savedState = loadState();

    if (!extra.length) {
        extrasW.style.display = 'none';
        return;
    }

    extrasW.style.display = '';
    extra.forEach(f => {
        const fieldHtml = createFieldHtml(f, savedState || {});
        formE.insertAdjacentHTML('beforeend', fieldHtml);
    });
    formE.oninput = () => {
        saveState();
        updatePreview();
    };
}

function createFieldHtml(field, savedValues = {}) {
    const savedValue = savedValues[field.name];

    if (field.type === 'bool') {
        const isChecked = savedValue !== undefined ? savedValue : (field.default || false);
        return `
            <div class="field checkbox">
                <label>
                    <input
                        type="checkbox"
                        name="${field.name}"
                        ${isChecked ? 'checked' : ''}
                    />
                    ${field.name}
                </label>
            </div>
        `;
    } else {
        const value = savedValue !== undefined ? savedValue : (field.default || '');
        return `
            <div class="field">
                <label>${field.name} (${field.type})</label>
                <input
                    type="text"
                    name="${field.name}"
                    value="${value}"
                />
            </div>
        `;
    }
}

function collect() {
    const data = { __connector: current.name, __sub: current.sub };

    [globalsW, extrasW].forEach(container => {
        container.querySelectorAll('input').forEach(i => {
            const name = i.name;
            if (i.type === 'checkbox') {
                data[name] = i.checked;
            } else if (i.value !== '') {
                data[name] = i.value;
            }
        });
    });

    return data;
}

async function updatePreview() {
    if (!current.name) return;

    previewContent.value = previewContent.value;

    try {
        const res = await fetch('/preview', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(collect())
        });

        const js = await res.json();
        previewContent.value = js.command || js.error;
    } catch (e) {
        previewContent.value = e.message;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    buildMenu();

    const lastSelected = localStorage.getItem('lastSelectedSub');
    if (lastSelected) {
        const { name, sub } = JSON.parse(lastSelected);
        selectSub(name, sub);
    }
});