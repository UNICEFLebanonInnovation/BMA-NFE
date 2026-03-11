(function() {
  const cellSize = 22;
  const margin = { top: 30, left: 40, right: 20, bottom: 10 };
  const monthNames = window.trans.months || ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];

  function prepareData(raw) {
    return (raw || []).map(d => {
      const date = new Date(d.attendance_day__attendance_date);
      const total = Number(d.total) || 0;
      const absent = Number(d.absent) || 0;
      const present = total - absent;
      const rate = total ? present / total : 0;
      const percentage = rate * 100;
      return { date, present, total, rate, percentage };
    });
  }

  function createLegend(selector) {
    const legendWidth = 200;
    const legendHeight = 10;

    const svg = d3.select(selector).append('svg')
      .attr('width', legendWidth)
      .attr('height', legendHeight + 20);

    const color = d3.scaleSequential()
      .domain([0, 100])
      .interpolator(d3.interpolateGreens);

    const legendScale = d3.scaleLinear()
      .domain([0, 100])
      .range([0, legendWidth]);

    const legendData = d3.range(0, 101, 1);

    svg.selectAll('rect')
      .data(legendData)
      .enter()
      .append('rect')
      .attr('x', d => legendScale(d))
      .attr('y', 0)
      .attr('width', legendWidth / legendData.length + 1)
      .attr('height', legendHeight)
      .attr('fill', d => color(d));

    svg.append('g')
      .attr('transform', `translate(0, ${legendHeight})`)
      .attr('class', 'legend-axis')
      .call(d3.axisBottom(legendScale).ticks(5).tickFormat(d => d + '%'))
      .style('font-size', '8px')
      .select('.domain').remove();
  }

  function renderHeatmap(selector, rawData) {
    const data = prepareData(rawData);
    if (!data.length) {
      d3.select(selector).html('<div class="alert alert-light text-center my-4">No data available for this selection.</div>');
      return;
    }

    const width = cellSize * 31 + margin.left + margin.right;
    const height = cellSize * 12 + margin.top + margin.bottom;

    const svg = d3.select(selector).append('svg')
      .attr('viewBox', `0 0 ${width} ${height}`)
      .attr('preserveAspectRatio', 'xMinYMin meet')
      .classed('w-100', true)
      .style('max-width', `${width}px`);

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    const color = d3.scaleSequential()
      .domain([0, 100])
      .interpolator(d3.interpolateGreens);

    const tooltip = d3.select('body').selectAll('.heatmap-tooltip').data([0]).enter()
      .append('div')
      .attr('class', 'heatmap-tooltip shadow-sm bg-white p-2 border position-absolute')
      .style('opacity', 0)
      .style('pointer-events', 'none')
      .style('z-index', 1000);

    g.selectAll('rect')
      .data(data)
      .enter()
      .append('rect')
      .attr('x', d => (d.date.getDate() - 1) * cellSize)
      .attr('y', d => d.date.getMonth() * cellSize)
      .attr('width', cellSize - 2)
      .attr('height', cellSize - 2)
      .attr('rx', 2)
      .attr('ry', 2)
      .attr('fill', d => d.total === 0 ? '#f8f9fa' : color(d.percentage))
      .attr('stroke', '#eee')
      .attr('stroke-width', 1)
      .on('mouseover', function(event, d) {
        d3.select(this).attr('stroke', '#004F71').attr('stroke-width', 2);
        const text = `<strong>${d3.timeFormat('%Y-%m-%d')(d.date)}</strong><br/>
                      ${window.trans.present}: ${d.present}<br/>
                      ${window.trans.total}: ${d.total}<br/>
                      <span class="text-success fw-bold">${d.percentage.toFixed(1)}%</span>`;
        tooltip.transition().duration(200).style('opacity', 1);
        tooltip.html(text)
          .style('left', (event.pageX + 10) + 'px')
          .style('top', (event.pageY - 20) + 'px');
      })
      .on('mousemove', function(event) {
        tooltip.style('left', (event.pageX + 10) + 'px')
               .style('top', (event.pageY - 20) + 'px');
      })
      .on('mouseout', function() {
        d3.select(this).attr('stroke', '#eee').attr('stroke-width', 1);
        tooltip.transition().duration(500).style('opacity', 0);
      });

    // Month Labels
    g.selectAll('text.month')
      .data(monthNames)
      .enter()
      .append('text')
      .attr('class', 'month small')
      .attr('x', -10)
      .attr('y', (d, i) => i * cellSize + cellSize / 1.5)
      .attr('text-anchor', 'end')
      .attr('font-size', '11px')
      .text(d => d);

    // Day Labels
    const days = Array.from({ length: 31 }, (_, i) => i + 1);
    g.selectAll('text.day')
      .data(days)
      .enter()
      .append('text')
      .attr('class', 'day small')
      .attr('x', (d, i) => i * cellSize + cellSize / 2)
      .attr('y', -10)
      .attr('text-anchor', 'middle')
      .attr('font-size', '10px')
      .text(d => d);
  }

  // Initial render
  createLegend('#heatmap-legend-container');
  renderHeatmap('#attendance-heatmap', window.attendanceData);

  // Render programme-specific heatmaps
  const programmeData = window.programAttendanceData || {};
  const container = d3.select('#programme-heatmaps-container');

  Object.keys(programmeData).forEach(programme => {
    const slug = programme.toLowerCase().replace(/[^a-z0-9]+/g, '-');

    const card = container.append('div')
      .attr('class', 'card shadow-sm border-0 mb-4');

    card.append('div')
      .attr('class', 'card-header bg-white py-3')
      .append('h5')
      .attr('class', 'mb-0 fw-bold text-dark')
      .html(`<i class="bi bi-collection text-primary me-2"></i> ${programme}`);

    const divId = `heatmap-${slug}`;
    card.append('div')
      .attr('class', 'card-body')
      .append('div')
      .attr('id', divId)
      .attr('class', 'heatmap-container');

    renderHeatmap(`#${divId}`, programmeData[programme]);
  });
})();
