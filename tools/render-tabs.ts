// Fixed publisher code, hashed by the preview CSP. Authored HTML supplies only
// labelled sections and scalar selection values; it never supplies executable code.
export const tabsController = String.raw`(() => {
  const widgets = Array.from(document.querySelectorAll('[data-tabs]')).map((group, groupIndex) => {
    const panels = Array.from(group.children).filter(child => child.matches('section[data-tab]'));
    if (!panels.length) return null;
    const list = document.createElement('div');
    list.setAttribute('role', 'tablist');
    list.setAttribute('aria-label', group.getAttribute('aria-label') || 'Examples');
    const buttons = panels.map((panel, index) => {
      const button = document.createElement('button');
      const heading = panel.querySelector('header, h2, h3, h4');
      panel.id ||= 'preview-panel-' + groupIndex + '-' + index;
      button.id = panel.id + '-tab';
      button.type = 'button';
      button.textContent = heading ? heading.textContent : panel.dataset.tab;
      button.setAttribute('role', 'tab');
      button.setAttribute('aria-controls', panel.id);
      panel.setAttribute('role', 'tabpanel');
      panel.setAttribute('aria-labelledby', button.id);
      panel.tabIndex = 0;
      list.append(button);
      return button;
    });
    const select = index => {
      panels.forEach((panel, position) => {
        panel.hidden = position !== index;
        buttons[position].setAttribute('aria-selected', String(position === index));
        buttons[position].tabIndex = position === index ? 0 : -1;
      });
    };
    const activate = (index, focus) => {
      select(index);
      if (focus) buttons[index].focus();
      if (group.dataset.group) widgets.forEach(other => {
        if (!other || other.group === group || other.group.dataset.group !== group.dataset.group) return;
        const match = other.panels.findIndex(panel => panel.dataset.tab === panels[index].dataset.tab);
        if (match >= 0) other.select(match);
      });
    };
    buttons.forEach((button, index) => {
      button.addEventListener('click', () => activate(index, false));
      button.addEventListener('keydown', event => {
        const next = event.key === 'ArrowRight' ? (index + 1) % panels.length
          : event.key === 'ArrowLeft' ? (index + panels.length - 1) % panels.length
          : event.key === 'Home' ? 0 : event.key === 'End' ? panels.length - 1 : null;
        if (next === null) return;
        event.preventDefault();
        activate(next, true);
      });
    });
    group.prepend(list);
    const initial = panels.findIndex(panel => panel.dataset.tab === group.dataset.default);
    select(initial < 0 ? 0 : initial);
    return {group, panels, select};
  });
})();`;
