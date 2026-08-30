(function () {
  'use strict';

  const config = window.alpTeacherDashboardConfig;
  const chartColors = d3.schemeTableau10;

  function selectedValues(id) {
    const element = document.getElementById(id);
    return element ? Array.from(element.selectedOptions).map(option => option.value) : [];
  }

  function queryString() {
    const params = new URLSearchParams();
    selectedValues('schoolFilter').forEach(value => params.append('schools', value));
    selectedValues('roundFilter').forEach(value => params.append('rounds', value));
    return params.toString();
  }

  function emptyState(root) {
    root.append('div').attr('class', 'text-center text-muted pt-5').text(config.noData);
  }

  function renderPie(selector, data) {
    const root = d3.select(selector);
    root.selectAll('*').remove();
    if (!data || !data.length) return emptyState(root);

    const width = root.node().clientWidth || 320;
    const height = 250;
    const radius = Math.min(width, height) / 2 - 20;
    const color = d3.scaleOrdinal(chartColors);
    const svg = root.append('svg').attr('width', width).attr('height', height)
      .append('g').attr('transform', `translate(${width / 2},${height / 2})`);
    const arc = d3.arc().innerRadius(radius * .5).outerRadius(radius);

    svg.selectAll('path').data(d3.pie().value(item => item.y)(data)).enter().append('path')
      .attr('d', arc).attr('fill', item => color(item.data.name)).attr('stroke', '#fff')
      .append('title').text(item => `${item.data.name}: ${item.data.y}`);

    const legend = root.append('div').attr('class', 'd-flex flex-wrap justify-content-center gap-3 small');
    data.forEach(item => legend.append('span').text(`${item.name}: ${item.y}`));
  }

  function renderBar(selector, data) {
    const root = d3.select(selector);
    root.selectAll('*').remove();
    if (!data || !data.length) return emptyState(root);

    const fullWidth = root.node().clientWidth || 400;
    const margin = {top: 15, right: 10, bottom: 95, left: 45};
    const width = fullWidth - margin.left - margin.right;
    const height = 300 - margin.top - margin.bottom;
    const svg = root.append('svg').attr('width', fullWidth).attr('height', 300)
      .append('g').attr('transform', `translate(${margin.left},${margin.top})`);
    const x = d3.scaleBand().domain(data.map(item => item.name)).range([0, width]).padding(.2);
    const y = d3.scaleLinear().domain([0, d3.max(data, item => item.y) || 1]).nice().range([height, 0]);

    svg.append('g').attr('transform', `translate(0,${height})`).call(d3.axisBottom(x))
      .selectAll('text').attr('transform', 'rotate(-35)').style('text-anchor', 'end');
    svg.append('g').call(d3.axisLeft(y).ticks(5));
    svg.selectAll('rect').data(data).enter().append('rect')
      .attr('x', item => x(item.name)).attr('y', item => y(item.y))
      .attr('width', x.bandwidth()).attr('height', item => height - y(item.y))
      .attr('fill', (item, index) => chartColors[index % chartColors.length])
      .append('title').text(item => `${item.name}: ${item.y}`);
  }

  function setText(id, value) {
    document.getElementById(id).textContent = value;
  }

  async function refresh() {
    const loading = document.getElementById('dashboardLoading');
    const error = document.getElementById('dashboardError');
    loading.classList.remove('d-none');
    error.classList.add('d-none');

    try {
      const response = await fetch(`${config.dataUrl}?${queryString()}`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();

      setText('kpiTotal', data.total);
      setText('kpiSchools', data.schools);
      setText('kpiTrained', data.trained);
      setText('kpiTrainedPercent', `${data.trained_percent}%`);
      setText('kpiExperience', data.average_experience);
      setText('kpiSessions', data.average_sessions);
      setText('kpiContact', `${data.contact_percent}%`);

      renderPie('#chartGender', data.gender);
      renderPie('#chartNationality', data.nationality);
      renderPie('#chartAssignment', data.assignment);
      renderBar('#chartSchool', data.school);
      renderBar('#chartRound', data.round);
      renderBar('#chartSubjects', data.subjects);
      renderBar('#chartLevels', data.levels);
      renderBar('#chartTrainings', data.trainings);
      renderBar('#chartHours', data.hours);
      renderPie('#chartCoaching', data.coaching);
    } catch (exception) {
      console.error(exception);
      error.textContent = config.error;
      error.classList.remove('d-none');
    } finally {
      loading.classList.add('d-none');
    }
  }

  $('.selectpicker').selectpicker();
  document.getElementById('applyFilters').addEventListener('click', refresh);
  document.getElementById('resetFilters').addEventListener('click', function () {
    $('.selectpicker').selectpicker('deselectAll').selectpicker('refresh');
    refresh();
  });
  refresh();
}());
