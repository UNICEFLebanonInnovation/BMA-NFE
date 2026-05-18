(function () {
  'use strict';

  const state = {
    filters: {},
  };

  const config = window.wellbeingDashboardConfig;
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
    const containerWidth = root.node().getBoundingClientRect().width;
    const width = containerWidth, height = 300, radius = Math.min(width, height) / 2 - 40;

    const svg = root.append('svg')
      .attr('width', width)
      .attr('height', height)
      .append('g')
      .attr('transform', `translate(${width / 2},${height / 2})`);

    const color = d3.scaleOrdinal(d3.schemeTableau10);
    const pie = d3.pie().value(d => d.y);
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
        tooltip.html(`${d.data.name}: ${d.data.y}`)
          .style("left", (event.pageX) + "px")
          .style("top", (event.pageY - 28) + "px");
      })
      .on("mouseout", function() {
        tooltip.transition().duration(500).style("opacity", 0);
      });

    // Simple Legend
    const legend = root.append('div').attr('class', 'mt-3 d-flex flex-wrap justify-content-center gap-2');
    data.forEach(d => {
      const item = legend.append('div').attr('class', 'small d-flex align-items-center');
      item.append('span').style('display', 'inline-block').style('width', '10px').style('height', '10px').style('background-color', color(d.name)).attr('class', 'me-1');
      item.append('span').text(d.name);
    });
  }


  function wrapText(text, width) {
    text.each(function() {
      var text = d3.select(this),
          words = text.text().split(/\s+/).reverse(),
          word,
          line = [],
          lineNumber = 0,
          lineHeight = 1.1, // ems
          y = text.attr("y"),
          dy = parseFloat(text.attr("dy")),
          tspan = text.text(null).append("tspan").attr("x", 0).attr("y", y).attr("dy", dy + "em");
      while (word = words.pop()) {
        line.push(word);
        tspan.text(line.join(" "));
        if (tspan.node().getComputedTextLength() > width && line.length > 1) {
          line.pop();
          tspan.text(line.join(" "));
          line = [word];
          tspan = text.append("tspan").attr("x", 0).attr("y", y).attr("dy", ++lineNumber * lineHeight + dy + "em").text(word);
        }
      }
    });
  }

  function renderBarChart(selector, data, isHorizontal = false) {
    const root = d3.select(selector);
    if (!root.node()) return;
    root.selectAll('*').remove();
    const margin = { top: 20, right: 30, bottom: 60, left: 60 };
    const width = root.node().getBoundingClientRect().width - margin.left - margin.right;
    const height = 300 - margin.top - margin.bottom;

    const svg = root.append('svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    const yMin = d3.min(data, d => d.y);
    const yMax = d3.max(data, d => d.y) || 10;

    const x = d3.scaleBand().range([0, width]).domain(data.map(d => d.name)).padding(0.3);
    const y = d3.scaleLinear().range([height, 0]).domain([Math.min(0, yMin), Math.max(0, yMax)]);

    svg.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(x))
      .selectAll('text')
      .call(wrapText, x.bandwidth());

    svg.append('g').call(d3.axisLeft(y).ticks(5));

    svg.selectAll('bar')
      .data(data)
      .enter()
      .append('rect')
      .attr('x', d => x(d.name))
      .attr('width', x.bandwidth())
      .attr('y', d => y(Math.max(0, d.y)))
      .attr('height', d => Math.abs(y(d.y) - y(0)))
      .attr('fill', '#00adef')
      .on("mouseover", function(event, d) {
        tooltip.transition().duration(200).style("opacity", .9);
        tooltip.html(`${d.name}: ${d.y}`)
          .style("left", (event.pageX) + "px")
          .style("top", (event.pageY - 28) + "px");
      })
      .on("mouseout", function() {
        tooltip.transition().duration(500).style("opacity", 0);
      });

    // Add zero line if there are negative values
    if (yMin < 0) {
      svg.append('line')
        .attr('x1', 0)
        .attr('x2', width)
        .attr('y1', y(0))
        .attr('y2', y(0))
        .attr('stroke', '#000')
        .attr('stroke-width', 1);
    }
  }

  function renderImprovementChart(selector, data) {
    const root = d3.select(selector);
    if (!root.node()) return;
    root.selectAll('*').remove();

    if (!data || data.length === 0) {
        root.append('div').attr('class', 'text-muted text-center p-5').text('No data available');
        return;
    }

    const margin = { top: 30, right: 30, bottom: 60, left: 120 };
    const width = root.node().getBoundingClientRect().width - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;

    const svg = root.append('svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    const programs = Array.from(new Set(data.map(d => d.programme)));
    const materials = Array.from(new Set(data.map(d => d.material)));

    const x0 = d3.scaleBand()
      .domain(programs)
      .rangeRound([0, width])
      .paddingInner(0.1);

    const x1 = d3.scaleBand()
      .domain(materials)
      .rangeRound([0, x0.bandwidth()])
      .padding(0.05);

    const yMin = d3.min(data, d => d.improvement);
    const yMax = d3.max(data, d => d.improvement) || 20;

    const y = d3.scaleLinear()
      .domain([Math.min(0, yMin), Math.max(0, yMax)]).nice()
      .rangeRound([height, 0]);

    const color = d3.scaleOrdinal(d3.schemeCategory10).domain(materials);

    svg.append('g')
      .selectAll('g')
      .data(programs)
      .enter().append('g')
      .attr('transform', d => `translate(${x0(d)},0)`)
      .selectAll('rect')
      .data(d => data.filter(item => item.programme === d))
      .enter().append('rect')
      .attr('x', d => x1(d.material))
      .attr('y', d => y(Math.max(0, d.improvement)))
      .attr('width', x1.bandwidth())
      .attr('height', d => Math.abs(y(d.improvement) - y(0)))
      .attr('fill', d => color(d.material))
      .on("mouseover", function(event, d) {
        tooltip.transition().duration(200).style("opacity", .9);
        tooltip.html(`<strong>${d.programme}</strong><br>${d.material}: ${d.improvement}%`)
          .style("left", (event.pageX) + "px")
          .style("top", (event.pageY - 28) + "px");
      })
      .on("mouseout", function() {
        tooltip.transition().duration(500).style("opacity", 0);
      });

    // Add zero line if there are negative values
    if (yMin < 0) {
      svg.append('line')
        .attr('x1', 0)
        .attr('x2', width)
        .attr('y1', y(0))
        .attr('y2', y(0))
        .attr('stroke', '#000')
        .attr('stroke-width', 1);
    }

    svg.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(x0))
      .selectAll('text')
      .attr('transform', 'translate(-10,0)rotate(-25)')
      .style('text-anchor', 'end');

    svg.append('g')
      .call(d3.axisLeft(y).ticks(5).tickFormat(d => d + '%'));

    // Legend
    const legend = root.append('div').attr('class', 'mt-3 d-flex flex-wrap justify-content-center gap-3');
    materials.forEach(m => {
      const item = legend.append('div').attr('class', 'small d-flex align-items-center');
      item.append('span').style('display', 'inline-block').style('width', '12px').style('height', '12px').style('background-color', color(m)).attr('class', 'me-1');
      item.append('span').text(m);
    });
  }

  function renderPSSIndicators(selector, data) {
    const root = d3.select(selector);
    if (!root.node()) return;
    root.selectAll('*').remove();
    const items = [
        { label: 'Caregiver Distress', value: data.caregiver_distress, color: '#ffc107' },
        { label: 'Child Distress', value: data.child_distress, color: '#fd7e14' },
    ];

    const container = root.append('div').attr('class', 'row g-4 text-center py-4');
    items.forEach(item => {
        const col = container.append('div').attr('class', 'col-md-6');
        col.append('div').attr('class', 'h1 fw-bold').style('color', item.color).text(item.value);
        col.append('div').attr('class', 'text-muted small text-uppercase').text(item.label);
    });
  }

  function renderGroupedBar(selector, matrix) {
    // For Labor Type & Income
    const root = d3.select(selector);
    if (!root.node()) return;
    root.selectAll('*').remove();
    // Simplified: show top types
    const types = Array.from(new Set(matrix.map(d => d.type))).slice(0, 5);
    const summary = types.map(t => ({
        name: t,
        y: matrix.filter(m => m.type === t).reduce((acc, curr) => acc + curr.count, 0)
    }));
    renderBarChart(selector, summary);
  }

  async function refresh() {
    const data = await fetchData();

    // Update KPIs
    const kpiAvgAttendance = document.getElementById('kpi_avg_attendance');
    if (kpiAvgAttendance) kpiAvgAttendance.innerText = `${data.kpis.avg_attendance}%`;

    const kpiLaborRate = document.getElementById('kpi_labor_rate');
    if (kpiLaborRate) kpiLaborRate.innerText = `${data.kpis.labor_rate}%`;

    const kpiAvgImprovement = document.getElementById('kpi_avg_improvement');
    if (kpiAvgImprovement) kpiAvgImprovement.innerText = `${data.kpis.avg_improvement}%`;


    const kpiNfeToFe = document.getElementById('kpi_nfe_to_fe');
    if (kpiNfeToFe) kpiNfeToFe.innerText = `${data.transitions.nfe_to_fe}`;

    const kpiAvgNfeGrade = document.getElementById('kpi_avg_nfe_grade');
    if (kpiAvgNfeGrade) kpiAvgNfeGrade.innerText = `${data.transitions.avg_nfe_grade}%`;

    const kpiDropoutRate = document.getElementById('kpi_dropout_rate');
    if (kpiDropoutRate) kpiDropoutRate.innerText = `${data.transitions.dropout_rate}%`;

    const kpiEligibleForFe = document.getElementById('kpi_eligible_for_fe');
    if (kpiEligibleForFe) kpiEligibleForFe.innerText = `${data.transitions.eligible_for_fe_count}`;

    // Populate FE Eligible List Modal
    const feTableBody = document.getElementById('feEligibleTableBody');
    if (feTableBody) {
        if (data.transitions.eligible_for_fe_list && data.transitions.eligible_for_fe_list.length > 0) {
            feTableBody.innerHTML = data.transitions.eligible_for_fe_list.map(child => `
                <tr>
                    <td class="align-middle">${child.case_number || 'N/A'}</td>
                    <td class="align-middle fw-medium">${child.child_name || 'N/A'}</td>
                    <td class="align-middle text-muted">${child.age !== null ? child.age : '-'}</td>
                    <td class="align-middle text-end">
                        <a href="/mscc/child-profile/${child.reg_id}/" target="_blank" class="btn btn-sm btn-outline-primary">
                            <i class="bi bi-eye"></i> View
                        </a>
                    </td>
                </tr>
            `).join('');
        } else {
            feTableBody.innerHTML = `
                <tr>
                    <td colspan="4" class="text-center py-4 text-muted">No children eligible for Formal Education at this time.</td>
                </tr>
            `;
        }
    }

    // Render Charts
    renderPieChart('#chart_child_labor', data.socio_economic.labor_participation);
    renderGroupedBar('#chart_labor_income', data.socio_economic.labor_income);
    renderBarChart('#chart_cash_support', data.socio_economic.cash_support);

    renderPieChart('#chart_living_arrangements', data.wellbeing.living_arrangements);
    renderPieChart('#chart_birth_registration', data.wellbeing.birth_registration);
    renderBarChart('#chart_vulnerabilities', data.wellbeing.vulnerabilities);
    renderPSSIndicators('#chart_pss_indicators', data.wellbeing.pss_indicators);

    renderBarChart('#chart_education_status', data.education.status);
    renderImprovementChart('#chart_programme_improvements', data.education.programme_improvements);

    // NFE platforms transition
    if (document.getElementById('chart_nfe_platforms')) {
        renderBarChart('#chart_nfe_platforms', data.transitions.nfe_platforms);
    }

    // Drop Out Rate by Program
    if (document.getElementById('chart_dropout_by_program')) {
        renderBarChart('#chart_dropout_by_program', data.transitions.dropout_by_program, 'Drop Out Rate (%)');
    }


    // Impact: Attendance vs Improvement
    renderBarChart('#impact_attendance_improvement', [
        { name: 'High Attendance (>95%)', y: data.impact.attendance_impact_improvement.high_attendance },
        { name: 'Low Attendance (<70%)', y: data.impact.attendance_impact_improvement.low_attendance }
    ]);

    // Impact: Labor vs Attendance
    renderBarChart('#impact_labor_attendance', [
        { name: 'With Labor', y: data.impact.labor_impact_attendance.with_labor },
        { name: 'Without Labor', y: data.impact.labor_impact_attendance.without_labor }
    ]);

    // NEW CORRELATIONS
    if (document.getElementById('impact_distress_attendance')) {
        renderBarChart('#impact_distress_attendance', [
            { name: 'With Distress', y: data.impact.distress_impact_attendance.with_distress },
            { name: 'Without Distress', y: data.impact.distress_impact_attendance.without_distress }
        ]);
    }

    if (document.getElementById('impact_cash_labor')) {
        renderBarChart('#impact_cash_labor', [
            { name: 'With Cash Support', y: data.impact.cash_impact_labor.with_cash_support },
            { name: 'Without Cash Support', y: data.impact.cash_impact_labor.without_cash_support }
        ]);
    }
  }

  const applyFiltersBtn = document.getElementById('applyFilters');
  if (applyFiltersBtn) applyFiltersBtn.addEventListener('click', refresh);

  const refreshDataBtn = document.getElementById('refreshData');
  if (refreshDataBtn) refreshDataBtn.addEventListener('click', refresh);

  refresh();

  window.addEventListener('resize', refresh);


  // Handle metric-card clicks
  document.querySelectorAll('.metric-card').forEach(card => {
    card.addEventListener('click', async function() {
      const indicator = this.dataset.indicator;
      if (!indicator) return;

      const titleMap = {
          'avg_attendance': 'Avg Attendance Rate',
          'labor_rate': 'Child Labor Rate',
          'nfe_to_fe': 'Transition NFE to FE',
          'avg_nfe_grade': 'Avg NFE Grade Impr.',
          'dropout_rate': 'Avg Drop Out Rate'
      };

      const modalTitle = document.getElementById('indicatorChildrenModalLabel');
      if (modalTitle) modalTitle.innerText = `Children List: ${titleMap[indicator] || indicator}`;

      const tbody = document.getElementById('indicatorChildrenTableBody');
      if (tbody) {
          tbody.innerHTML = `
              <tr>
                  <td colspan="4" class="text-center py-4 text-muted">
                      <div class="spinner-border spinner-border-sm me-2" role="status"></div>
                      Loading data...
                  </td>
              </tr>
          `;
      }

      // Show modal
      const modalEl = document.getElementById('indicatorChildrenModal');
      const modal = new bootstrap.Modal(modalEl);
      modal.show();

      // Fetch data
      const filters = getFilters();
      const params = new URLSearchParams();
      for (const key in filters) {
        filters[key].forEach(v => params.append(key, v));
      }
      params.append('indicator', indicator);

      try {
          const response = await fetch(`${config.urls.indicator_children_data}?${params.toString()}`);
          const data = await response.json();

          if (tbody) {
              if (data.children && data.children.length > 0) {
                  tbody.innerHTML = data.children.map(child => `
                      <tr>
                          <td class="align-middle">${child.case_number || 'N/A'}</td>
                          <td class="align-middle fw-medium">${child.child_name || 'N/A'}</td>
                          <td class="align-middle text-muted">${child.age !== null ? child.age : '-'}</td>
                          <td class="align-middle text-end">
                              <a href="/mscc/child-profile/${child.reg_id}/" target="_blank" class="btn btn-sm btn-outline-primary">
                                  <i class="bi bi-eye"></i> View
                              </a>
                          </td>
                      </tr>
                  `).join('');
              } else {
                  tbody.innerHTML = `
                      <tr>
                          <td colspan="4" class="text-center py-4 text-muted">No children found for this indicator.</td>
                      </tr>
                  `;
              }
          }
      } catch (e) {
          if (tbody) {
              tbody.innerHTML = `
                  <tr>
                      <td colspan="4" class="text-center py-4 text-danger">Failed to load data.</td>
                  </tr>
              `;
          }
      }
    });
  });
})();
