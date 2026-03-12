(function () {
  const state = {
    filters: {},
    selected: {},
  };

  const el = (id) => document.getElementById(id);
  const config = window.msccDashboardConfig;

  function getFilters() {
    const ids = ['center_filter', 'round_filter', 'governorate_filter', 'partner_filter'];
    ids.forEach((id) => {
      const element = el(id);
      if (element) {
        const values = Array.from(element.selectedOptions).map(opt => opt.value).filter(v => v);
        if (values.length > 0) state.filters[id.replace('_filter', '') + 's'] = values;
        else delete state.filters[id.replace('_filter', '') + 's'];
      }
    });
    return state.filters;
  }

  function toQuery(params) {
    const q = new URLSearchParams();
    for (const key in params) {
      if (Array.isArray(params[key])) {
        params[key].forEach(v => q.append(key, v));
      } else {
        q.append(key, params[key]);
      }
    }
    return `?${q.toString()}`;
  }

  async function fetchJson(url, params) {
    const response = await fetch(`${url}${toQuery(params)}`);
    return response.json();
  }

  function renderBarChart(selector, items, titleText) {
    const root = d3.select(selector);
    root.selectAll('*').remove();

    const containerWidth = root.node().getBoundingClientRect().width || 400;
    const margin = { top: 20, right: 20, bottom: 60, left: 50 };
    const width = containerWidth - margin.left - margin.right;
    const height = 300 - margin.top - margin.bottom;

    const svg = root.append('svg')
      .attr('width', containerWidth)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    const x = d3.scaleBand()
      .range([0, width])
      .domain(items.map(d => d.name))
      .padding(0.2);

    const y = d3.scaleLinear()
      .domain([0, d3.max(items, d => d.y) || 1])
      .nice()
      .range([height, 0]);

    svg.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(x))
      .selectAll('text')
      .attr('transform', 'translate(-10,0)rotate(-45)')
      .style('text-anchor', 'end');

    svg.append('g')
      .call(d3.axisLeft(y).ticks(5));

    svg.selectAll('rect')
      .data(items)
      .enter()
      .append('rect')
      .attr('x', d => x(d.name))
      .attr('y', d => y(d.y))
      .attr('width', x.bandwidth())
      .attr('height', d => height - y(d.y))
      .attr('fill', '#007bff')
      .append('title')
      .text(d => `${d.name}: ${d.y}`);
  }

  function renderPieChart(selector, items) {
    const root = d3.select(selector);
    root.selectAll('*').remove();

    const containerWidth = root.node().getBoundingClientRect().width || 400;
    const width = containerWidth, height = 300, radius = Math.min(width, height) / 2 - 40;

    const svg = root.append('svg')
      .attr('width', width)
      .attr('height', height)
      .append('g')
      .attr('transform', `translate(${width / 2},${height / 2})`);

    const color = d3.scaleOrdinal()
      .domain(items.map(d => d.name))
      .range(d3.schemeCategory10);

    const pie = d3.pie().value(d => d.y);
    const data_ready = pie(items);

    const arc = d3.arc().innerRadius(radius * 0.5).outerRadius(radius);

    svg.selectAll('path')
      .data(data_ready)
      .enter()
      .append('path')
      .attr('d', arc)
      .attr('fill', d => color(d.data.name))
      .attr('stroke', 'white')
      .style('stroke-width', '2px')
      .style('opacity', 0.7)
      .append('title')
      .text(d => `${d.data.name}: ${d.data.y}`);

    // Legend
    const legend = root.append('div').attr('class', 'd-flex flex-wrap justify-content-center mt-2');
    items.forEach(d => {
        const item = legend.append('div').attr('class', 'me-3 mb-1 small d-flex align-items-center');
        item.append('span').style('display', 'inline-block').style('width', '12px').style('height', '12px').style('background-color', color(d.name)).attr('class', 'me-1');
        item.append('span').text(`${d.name}: ${d.y}`);
    });
  }

  function renderStackedBarChart(selector, data) {
    const root = d3.select(selector);
    root.selectAll('*').remove();

    if (!data.categories || data.categories.length === 0) return;

    const containerWidth = root.node().getBoundingClientRect().width || 400;
    const margin = { top: 20, right: 20, bottom: 60, left: 50 };
    const width = containerWidth - margin.left - margin.right;
    const height = 300 - margin.top - margin.bottom;

    const svg = root.append('svg')
      .attr('width', containerWidth)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    const subgroups = ['moved', 'new'];
    const groups = data.categories;

    const stackedData = data.categories.map((cat, i) => ({
        group: cat,
        moved: data.moved[i],
        new: data.new[i]
    }));

    const x = d3.scaleBand()
      .domain(groups)
      .range([0, width])
      .padding([0.2]);

    svg.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(x).tickSizeOuter(0))
      .selectAll('text')
      .attr('transform', 'translate(-10,0)rotate(-45)')
      .style('text-anchor', 'end');

    const y = d3.scaleLinear()
      .domain([0, d3.max(stackedData, d => d.moved + d.new) || 1])
      .range([height, 0]);

    svg.append('g')
      .call(d3.axisLeft(y));

    const color = d3.scaleOrdinal()
      .domain(subgroups)
      .range(['#e83e8c', '#28a745']);

    const stackedSeries = d3.stack().keys(subgroups)(stackedData);

    svg.append('g')
      .selectAll('g')
      .data(stackedSeries)
      .enter().append('g')
      .attr('fill', d => color(d.key))
      .selectAll('rect')
      .data(d => d)
      .enter().append('rect')
      .attr('x', d => x(d.data.group))
      .attr('y', d => y(d[1]))
      .attr('height', d => y(d[0]) - y(d[1]))
      .attr('width', x.bandwidth())
      .append('title')
      .text(d => `${d.data.group}: ${d[1] - d[0]}`);

    // Legend
    const legend = root.append('div').attr('class', 'd-flex justify-content-center mt-2');
    subgroups.forEach(sub => {
        const item = legend.append('div').attr('class', 'me-3 small d-flex align-items-center');
        item.append('span').style('display', 'inline-block').style('width', '12px').style('height', '12px').style('background-color', color(sub)).attr('class', 'me-1');
        item.append('span').text(sub.charAt(0).toUpperCase() + sub.slice(1));
    });
  }

  async function refresh() {
    const filters = getFilters();
    const data = await fetchJson(config.urls.data, filters);

    renderPieChart('#children_per_gender', data.children_per_gender || []);
    renderPieChart('#children_per_status', data.children_per_status || []);
    renderPieChart('#children_per_disability', data.children_per_disability || []);
    renderPieChart('#children_cash_support', data.children_cash_support || []);

    renderBarChart('#children_per_programme', data.children_per_programme || []);
    renderBarChart('#children_per_nationality', data.children_per_nationality || []);
    renderBarChart('#children_per_source', data.children_per_source || []);
    renderBarChart('#children_per_vulnerability', data.children_per_vulnerability || []);
    renderBarChart('#children_volunteering', data.children_volunteering || []);
    renderBarChart('#children_per_round', data.children_per_round || []);

    renderStackedBarChart('#children_moved_rounds', data.children_moved_rounds || {});
  }

  function wireEvents() {
    ['center_filter', 'round_filter', 'governorate_filter', 'partner_filter'].forEach((id) => {
      const element = el(id);
      if (element) {
        element.addEventListener('change', refresh);
      }
    });
  }

  wireEvents();
  refresh();

  // Resize handling
  window.addEventListener('resize', refresh);
})();
