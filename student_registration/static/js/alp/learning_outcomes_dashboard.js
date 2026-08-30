(function () {
  const config = window.alpDashboardConfig;
  const colors = ['#198754', '#ffc107', '#dc3545'];

  function selectedFilters() {
    const filters = new URLSearchParams();
    ['school', 'round', 'programme'].forEach((name) => {
      const select = document.getElementById(`${name}_filter`);
      if (select) Array.from(select.selectedOptions).forEach(option => filters.append(`${name}s`, option.value));
    });
    return filters;
  }

  function donut(selector, items) {
    const root = d3.select(selector);
    root.selectAll('*').remove();
    const width = root.node().getBoundingClientRect().width || 300;
    const radius = Math.min(width, 220) / 2 - 15;
    const svg = root.append('svg').attr('width', width).attr('height', 220)
      .append('g').attr('transform', `translate(${width / 2},110)`);
    const color = d3.scaleOrdinal().domain(items.map(item => item.name)).range(colors);
    svg.selectAll('path').data(d3.pie().value(item => item.y)(items)).enter().append('path')
      .attr('d', d3.arc().innerRadius(radius * 0.55).outerRadius(radius))
      .attr('fill', item => color(item.data.name)).append('title')
      .text(item => `${item.data.name}: ${item.data.y}`);
    const legend = root.append('div').attr('class', 'small text-center');
    items.forEach(item => legend.append('span').attr('class', 'd-inline-block me-3')
      .text(`${item.name}: ${item.y}`));
  }

  function subjects(items) {
    const root = d3.select('#outcome-subjects');
    root.selectAll('*').remove();
    items.forEach(item => {
      const row = root.append('div').attr('class', 'mb-3');
      const label = row.append('div').attr('class', 'd-flex justify-content-between small mb-1');
      label.append('span').text(item.name);
      label.append('strong').text(`${item.y}%`);
      row.append('div').attr('class', 'progress').attr('role', 'progressbar')
        .attr('aria-label', item.name).attr('aria-valuenow', item.y)
        .attr('aria-valuemin', 0).attr('aria-valuemax', 100)
        .append('div').attr('class', 'progress-bar').style('width', `${item.y}%`);
    });
  }

  async function refresh() {
    const response = await fetch(`${config.urls.data}?${selectedFilters()}`);
    if (!response.ok) return;
    const outcome = (await response.json()).learning_outcomes;
    document.getElementById('outcome-assessed').textContent = outcome.assessed_children;
    document.getElementById('outcome-average').textContent = outcome.average_achievement === null ? '—' : `${outcome.average_achievement}%`;
    document.getElementById('outcome-follow-up').textContent = outcome.children_with_follow_up;
    document.getElementById('outcome-improved').textContent = outcome.improved_children;
    document.getElementById('learning-outcome-empty').classList.toggle('d-none', outcome.assessed_children > 0);
    document.getElementById('learning-outcome-charts').classList.toggle('d-none', outcome.assessed_children === 0);
    if (outcome.assessed_children) {
      donut('#outcome-bands', outcome.performance_bands);
      donut('#outcome-progress', outcome.progress);
      subjects(outcome.subjects);
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    ['school_filter', 'round_filter', 'programme_filter'].forEach((id) => {
      const select = document.getElementById(id);
      if (select) select.addEventListener('change', refresh);
    });
    refresh();
  });
})();
