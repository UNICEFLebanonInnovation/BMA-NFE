(function () {
  const state = {
    filters: { interval: 'month' },
    selected: {},
  };

  const el = (id) => document.getElementById(id);
  const config = window.analyticsConfig;

  function getFilters() {
    const ids = ['date_from', 'date_to', 'partner_id', 'center_id', 'programme_id'];
    ids.forEach((id) => {
      const value = el(id).value;
      if (value) state.filters[id] = value;
      else delete state.filters[id];
    });
    Object.assign(state.filters, state.selected);
    return state.filters;
  }

  function toQuery(params) {
    const q = new URLSearchParams(params);
    return `?${q.toString()}`;
  }

  async function fetchJson(url, params) {
    const response = await fetch(`${url}${toQuery(params)}`);
    return response.json();
  }

  function renderLineChart(selector, series) {
    const root = d3.select(selector);
    root.selectAll('*').remove();
    const width = 420, height = 220, margin = { top: 10, right: 10, bottom: 30, left: 40 };
    const svg = root.append('svg').attr('width', width).attr('height', height).attr('role', 'img').attr('aria-label', 'Trend chart');
    const x = d3.scalePoint().domain(series.map(d => d.period)).range([margin.left, width - margin.right]);
    const y = d3.scaleLinear().domain([0, d3.max(series, d => d.count) || 1]).nice().range([height - margin.bottom, margin.top]);
    svg.append('path').datum(series).attr('fill', 'none').attr('stroke', '#3f6ad8').attr('stroke-width', 2)
      .attr('d', d3.line().x(d => x(d.period)).y(d => y(d.count)));
    svg.append('g').attr('transform', `translate(0,${height - margin.bottom})`).call(d3.axisBottom(x).tickSizeOuter(0));
    svg.append('g').attr('transform', `translate(${margin.left},0)`).call(d3.axisLeft(y).ticks(5));
  }

  function renderHorizontalBar(selector, items, dimension) {
    const root = d3.select(selector); root.selectAll('*').remove();
    const width = 420, barHeight = 24, height = Math.max(120, items.length * barHeight + 40), margin = { top: 10, right: 10, bottom: 20, left: 140 };
    const svg = root.append('svg').attr('width', width).attr('height', height);
    const y = d3.scaleBand().domain(items.map(d => d.key)).range([margin.top, height - margin.bottom]).padding(0.2);
    const x = d3.scaleLinear().domain([0, d3.max(items, d => d.count) || 1]).nice().range([margin.left, width - margin.right]);

    svg.selectAll('rect').data(items).enter().append('rect')
      .attr('x', margin.left).attr('y', d => y(d.key)).attr('height', y.bandwidth())
      .attr('width', d => x(d.count) - margin.left)
      .attr('fill', '#16aaff').attr('tabindex', 0)
      .on('click', (_, d) => { state.selected[dimension] = d.key; refresh(); })
      .append('title').text(d => `${d.key}: ${d.count}`);

    svg.append('g').attr('transform', `translate(0,${height - margin.bottom})`).call(d3.axisBottom(x).ticks(4));
    svg.append('g').attr('transform', `translate(${margin.left},0)`).call(d3.axisLeft(y));
  }

  function renderHeatmap(selector, matrix) {
    const root = d3.select(selector); root.selectAll('*').remove();
    const width = 420, height = 260, margin = { top: 30, right: 10, bottom: 40, left: 80 };
    const svg = root.append('svg').attr('width', width).attr('height', height);
    const xVals = [...new Set(matrix.map(d => d.x))];
    const yVals = [...new Set(matrix.map(d => d.y))];
    const x = d3.scaleBand().domain(xVals).range([margin.left, width - margin.right]).padding(0.05);
    const y = d3.scaleBand().domain(yVals).range([margin.top, height - margin.bottom]).padding(0.05);
    const color = d3.scaleSequential(d3.interpolateBlues).domain([0, d3.max(matrix, d => d.count) || 1]);

    svg.selectAll('rect').data(matrix).enter().append('rect')
      .attr('x', d => x(d.x)).attr('y', d => y(d.y)).attr('width', x.bandwidth()).attr('height', y.bandwidth())
      .attr('fill', d => color(d.count)).append('title').text(d => `${d.x} / ${d.y}: ${d.count}`);
    svg.append('g').attr('transform', `translate(0,${height - margin.bottom})`).call(d3.axisBottom(x));
    svg.append('g').attr('transform', `translate(${margin.left},0)`).call(d3.axisLeft(y));
  }

  async function refresh() {
    const filters = getFilters();
    const [summary, trend, gender, nationality, crosstab] = await Promise.all([
      fetchJson(config.urls.summary, filters),
      fetchJson(config.urls.trend, filters),
      fetchJson(config.urls.breakdown, { ...filters, dimension: 'gender' }),
      fetchJson(config.urls.breakdown, { ...filters, dimension: 'nationality' }),
      fetchJson(config.urls.crosstab, { ...filters, x: 'programme', y: 'age' }),
    ]);

    el('kpi-total').textContent = summary.total_registrations;
    el('kpi-partners').textContent = summary.partners;
    el('kpi-centers').textContent = summary.centers;
    el('kpi-programmes').textContent = summary.programmes;

    renderLineChart('#chart-trend', trend.series || []);
    renderHorizontalBar('#chart-gender', gender.items || [], 'gender');
    renderHorizontalBar('#chart-nationality', nationality.items || [], 'nationality');
    renderHeatmap('#chart-crosstab', crosstab.matrix || []);
  }

  function wireEvents() {
    ['date_from', 'date_to', 'partner_id', 'center_id', 'programme_id'].forEach((id) => {
      el(id).addEventListener('change', refresh);
    });
    el('download-csv').addEventListener('click', () => {
      window.location = `${config.urls.exportCsv}${toQuery(getFilters())}`;
    });

    if (config.defaults.partner_id) el('partner_id').value = config.defaults.partner_id;
    if (config.defaults.center_id) el('center_id').value = config.defaults.center_id;
  }

  wireEvents();
  refresh();
})();
