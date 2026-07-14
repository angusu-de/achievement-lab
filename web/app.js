const API = 'https://api.github.com';
const form = document.querySelector('[data-lookup]');
const input = document.querySelector('#username');
const loading = document.querySelector('[data-loading]');
const profileHead = document.querySelector('[data-profile-head]');
const tabs = [...document.querySelectorAll('[data-tab]')];
const panes = [...document.querySelectorAll('[data-pane]')];

const number = (value) => new Intl.NumberFormat('en').format(Number(value || 0));
const node = (tag, className = '', text = '') => {
  const item = document.createElement(tag);
  if (className) item.className = className;
  if (text !== '') item.textContent = String(text);
  return item;
};

function selectTab(name) {
  tabs.forEach((tab) => tab.classList.toggle('is-active', tab.dataset.tab === name));
  panes.forEach((pane) => {
    const active = pane.dataset.pane === name;
    pane.hidden = !active;
    pane.classList.toggle('is-active', active);
  });
}

tabs.forEach((tab) => tab.addEventListener('click', () => selectTab(tab.dataset.tab)));

async function github(path, optional = false) {
  const response = await fetch(`${API}${path}`, {
    headers: {
      Accept: 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28'
    }
  });
  if (optional && response.status === 404) return null;
  if (!response.ok) {
    if (response.status === 404) throw new Error('That GitHub profile was not found.');
    if (response.status === 403 || response.status === 429) {
      throw new Error('GitHub’s public API limit was reached for this network. Try again later.');
    }
    throw new Error('GitHub could not be reached. Try again shortly.');
  }
  return response.json();
}

function buildData(profile, repos, profileRepo) {
  const active = repos.filter((repo) => !repo.fork && !repo.archived);
  const sum = (key) => active.reduce((total, repo) => total + Number(repo[key] || 0), 0);
  const count = active.length;
  const withDescription = active.filter((repo) => String(repo.description || '').trim()).length;
  const withTopics = active.filter((repo) => Array.isArray(repo.topics) && repo.topics.length).length;
  const withLicense = active.filter((repo) => repo.license && repo.license.spdx_id).length;
  const hasBio = Boolean(String(profile.bio || '').trim());
  const hasWebsite = Boolean(String(profile.blog || '').trim());
  const hasReadme = Boolean(profileRepo);

  const recommendations = [];
  if (!hasReadme) recommendations.push({ title: 'Create the username repository', detail: `${profile.login}/${profile.login} with a public root README.md.` });
  if (!hasBio) recommendations.push({ title: 'Write one clear profile promise', detail: 'Say what you build and who it helps in one sentence.' });
  if (!hasWebsite) recommendations.push({ title: 'Add one durable destination', detail: 'Link a portfolio or product page rather than a temporary campaign.' });
  if (count && withDescription < Math.min(count, 6)) recommendations.push({ title: 'Tighten repository descriptions', detail: 'Make the outcome clear before someone opens the README.' });
  if (count && withTopics < Math.min(count, 6)) recommendations.push({ title: 'Add precise repository topics', detail: 'Use problem, platform, implementation, and quality terms.' });
  if (count && withLicense < Math.min(count, 3)) recommendations.push({ title: 'Clarify reuse', detail: 'Add a license to public projects meant for others to use.' });
  if (!recommendations.length) recommendations.push({ title: 'Edit the proof shelf', detail: 'Pin up to six projects that each demonstrate a different strength.' });

  const highlights = [...active]
    .sort((a, b) => (b.stargazers_count - a.stargazers_count) || String(b.pushed_at).localeCompare(String(a.pushed_at)))
    .slice(0, 6);

  return {
    profile: {
      login: profile.login,
      name: profile.name || profile.login,
      bio: profile.bio || 'No public bio yet.',
      avatar: profile.avatar_url,
      url: profile.html_url,
      achievementUrl: `https://github.com/${encodeURIComponent(profile.login)}?tab=achievements`
    },
    stats: [
      ['Public repositories', profile.public_repos],
      ['Repository stars', sum('stargazers_count')],
      ['Followers', profile.followers],
      ['Active forks', sum('forks_count')]
    ],
    health: [
      ['Profile README', hasReadme],
      ['Public bio', hasBio],
      ['Website link', hasWebsite],
      ['Repository descriptions', count === 0 || withDescription >= Math.min(count, 6)],
      ['Repository topics', count === 0 || withTopics >= Math.min(count, 6)]
    ],
    recommendations,
    highlights,
    sample: repos.length
  };
}

function renderStats(items) {
  const target = document.querySelector('[data-stats]');
  target.replaceChildren(...items.map(([label, value]) => {
    const card = node('article', 'stat');
    card.append(node('strong', '', number(value)), node('span', '', label));
    return card;
  }));
}

function renderHealth(items) {
  document.querySelector('[data-health]').replaceChildren(...items.map(([label, ok]) => {
    const row = node('div', `health-row ${ok ? 'is-good' : ''}`);
    row.append(node('i', '', ok ? '✓' : '→'), node('span', '', label), node('small', '', ok ? 'Ready' : 'Open'));
    return row;
  }));
}

function renderPlan(items) {
  document.querySelector('[data-plan]').replaceChildren(...items.slice(0, 4).map((item) => {
    const row = node('label', 'plan-row');
    const check = document.createElement('input');
    check.type = 'checkbox';
    const copy = node('span');
    copy.append(node('strong', '', item.title), node('b', '', item.detail));
    row.append(check, copy);
    return row;
  }));
}

function renderRepos(items, sample) {
  document.querySelector('[data-project-note]').textContent = `${sample} public repos checked`;
  const target = document.querySelector('[data-repos]');
  if (!items.length) {
    target.replaceChildren(node('p', 'empty-state', 'No active public repositories found.'));
    return;
  }
  target.replaceChildren(...items.map((repo) => {
    const card = node('a', 'repo');
    card.href = repo.html_url;
    card.target = '_blank';
    card.rel = 'noopener';
    const meta = node('div', 'repo__meta');
    meta.append(node('span', '', repo.language || 'Mixed'), node('span', '', `★ ${number(repo.stargazers_count)}`));
    card.append(meta, node('strong', '', repo.name), node('p', '', repo.description || 'No description yet.'));
    return card;
  }));
}

function render(data) {
  const avatar = document.querySelector('[data-avatar]');
  avatar.src = data.profile.avatar;
  avatar.alt = `${data.profile.login}'s GitHub avatar`;
  document.querySelector('[data-name]').textContent = data.profile.name;
  document.querySelector('[data-bio]').textContent = data.profile.bio;
  document.querySelector('[data-profile]').href = data.profile.url;
  document.querySelector('[data-achievements]').href = data.profile.achievementUrl;
  renderStats(data.stats);
  renderHealth(data.health);
  renderPlan(data.recommendations);
  renderRepos(data.highlights, data.sample);
  loading.hidden = true;
  profileHead.hidden = false;
  selectTab('overview');
}

async function analyze(username, updateUrl = true) {
  const button = form.querySelector('button');
  form.querySelector('.form-error')?.remove();
  profileHead.hidden = true;
  panes.forEach((pane) => { pane.hidden = true; });
  loading.hidden = false;
  button.disabled = true;
  button.textContent = 'Reading…';
  try {
    const profile = await github(`/users/${encodeURIComponent(username)}`);
    const canonical = profile.login;
    const [repos, profileRepo] = await Promise.all([
      github(`/users/${encodeURIComponent(canonical)}/repos?type=owner&sort=updated&per_page=100`),
      github(`/repos/${encodeURIComponent(canonical)}/${encodeURIComponent(canonical)}`, true)
    ]);
    render(buildData(profile, repos, profileRepo));
    if (updateUrl) history.replaceState({}, '', `?user=${encodeURIComponent(canonical)}`);
  } catch (error) {
    loading.hidden = true;
    form.append(node('p', 'form-error', error.message));
  } finally {
    button.disabled = false;
    button.textContent = 'Analyze';
  }
}

form.addEventListener('submit', (event) => {
  event.preventDefault();
  const username = input.value.trim().replace(/^@/, '');
  if (/^[a-z\d](?:[a-z\d-]{0,37}[a-z\d])?$/i.test(username)) analyze(username);
  else {
    form.querySelector('.form-error')?.remove();
    form.append(node('p', 'form-error', 'Enter a valid GitHub username.'));
  }
});

const initial = new URLSearchParams(location.search).get('user') || document.body.dataset.defaultLogin;
input.value = initial;
analyze(initial, false);
