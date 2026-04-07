(function () {
  'use strict';

  const config = window.teacherDashboardConfig;
  const tooltip = d3.select("body").append("div").attr("class", "tooltip").style("opacity", 0);

  function getFilters() {
    const ids = ['center_filter', 'round_filter', 'governorate_filter', 'partner_filter'];
    const filters = {};
    ids.forEach((id) => {
      const element = document.getElementById(id);
      if (element) {
        const values = Array.from(element.selectedOptions).map(opt => opt.value).filter(v => v);
        if (values.length > 0) filters[id.replace('_filter', '') + 's'] = values;
      }
    });
    return filters;
  }

  async function fetchData() {
    const filters = getFilters();
    const params = new URLSearchParams();
    for (const key in filters) {
      filters[key].forEach(v => params.append(key, v));
    }
    const response = await fetch(`${config.urls.data}?${params.toString()}`);
    return await response.json();
  }

  function renderPieChart(selector, data) {
    const root = d3.select(selector);
    if (!root.node()) return;
    root.selectAll('*').remove();

    if (!data || data.length === 0) {
      root.append('div').attr('class', 'text-center text-muted mt-5').text('No data available');
      return;
    }

    const containerWidth = root.node().getBoundingClientRect().width;
    const width = containerWidth || 300, height = 300, radius = Math.min(width, height) / 2 - 40;

    const svg = root.append('svg')
      .attr('width', width)
      .attr('height', height)
      .append('g')
      .attr('transform', `translate(${width / 2},${height / 2})`);

    const color = d3.scaleOrdinal(d3.schemeTableau10);
    const pie = d3.pie().value(d => d.value);
    const arc = d3.arc().innerRadius(radius * 0.4).outerRadius(radius);

    const arcs = svg.selectAll('arc')
      .data(pie(data))
      .enter()
      .append('g');

    arcs.append('path')
      .attr('d', arc)
      .attr('fill', d => color(d.data.name))
      .attr('stroke', '#fff')
      .style('stroke-width', '2px')
      .on("mouseover", function(event, d) {
        tooltip.transition().duration(200).style("opacity", .9);
        tooltip.html(`${d.data.name}: ${d.data.value}`)
          .style("left", (event.pageX) + "px")
          .style("top", (event.pageY - 28) + "px");
      })
      .on("mouseout", function() {
        tooltip.transition().duration(500).style("opacity", 0);
      });

    // Legend
    const legend = root.append('div').attr('class', 'mt-3 d-flex flex-wrap justify-content-center gap-2');
    data.forEach(d => {
      const item = legend.append('div').attr('class', 'small d-flex align-items-center');
      item.append('span').style('display', 'inline-block').style('width', '10px').style('height', '10px').style('background-color', color(d.name)).attr('class', 'me-1');
      item.append('span').text(`${d.name} (${d.value})`);
    });
  }

  function renderBarChart(selector, data) {
    const root = d3.select(selector);
    if (!root.node()) return;
    root.selectAll('*').remove();

    if (!data || data.length === 0) {
      root.append('div').attr('class', 'text-center text-muted mt-5').text('No data available');
      return;
    }

    const containerWidth = root.node().getBoundingClientRect().width;
    const margin = {top: 20, right: 20, bottom: 60, left: 40};
    const width = (containerWidth || 400) - margin.left - margin.right;
    const height = 300 - margin.top - margin.bottom;

    const svg = root.append('svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    const x = d3.scaleBand()
      .range([0, width])
      .domain(data.map(d => d.name))
      .padding(0.2);

    const y = d3.scaleLinear()
      .domain([0, d3.max(data, d => d.value)])
      .range([height, 0]);

    svg.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(x))
      .selectAll("text")
      .attr("transform", "translate(-10,0)rotate(-45)")
      .style("text-anchor", "end");

    svg.append('g')
      .call(d3.axisLeft(y));

    const color = d3.scaleOrdinal(d3.schemeTableau10);

    svg.selectAll('mybar')
      .data(data)
      .enter()
      .append('rect')
      .attr('x', d => x(d.name))
      .attr('y', d => y(d.value))
      .attr('width', x.bandwidth())
      .attr('height', d => height - y(d.value))
      .attr('fill', d => color(d.name))
      .on("mouseover", function(event, d) {
        tooltip.transition().duration(200).style("opacity", .9);
        tooltip.html(`${d.name}: ${d.value}`)
          .style("left", (event.pageX) + "px")
          .style("top", (event.pageY - 28) + "px");
      })
      .on("mouseout", function() {
        tooltip.transition().duration(500).style("opacity", 0);
      });
  }

  async function init() {
    const data = await fetchData();

    document.getElementById('kpi_total_teachers').textContent = data.total_teachers;

    renderPieChart('#chart_gender', data.gender);
    renderPieChart('#chart_nationality', data.nationality);
    renderPieChart('#chart_round', data.round);
    renderPieChart('#chart_assignment', data.assignment);

    renderBarChart('#chart_subjects', data.subjects);
    renderBarChart('#chart_trainings', data.trainings);
    renderBarChart('#chart_training_frequency', data.training_frequency);
    renderBarChart('#chart_training_year', data.training_completion_year);
  }

  document.getElementById('applyFilters').addEventListener('click', init);
  document.getElementById('resetFilters').addEventListener('click', () => {
    setTimeout(init, 100);
  });

  // Initialize on load
  init();
})();