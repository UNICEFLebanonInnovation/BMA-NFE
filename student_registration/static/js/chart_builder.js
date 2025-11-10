(function(){
    'use strict';

    let rawData = [];
    let charts = [];
    let filters = {};
    let tooltip;
    let counter = 0;

    function loadMsccData(){
        const metric = document.getElementById('mscc-data-type').value;
        const update = () => {
            const data = aggregate(metric);
            document.getElementById('chart-data').value = JSON.stringify(data, null, 2);
        };
        if(rawData.length === 0){
            fetchData(update);
        }else{
            update();
        }
    }

    function showLoader(){
        document.getElementById('loading-indicator').style.display = 'block';
    }

    function hideLoader(){
        document.getElementById('loading-indicator').style.display = 'none';
    }

    function toggleFullscreen(id){
        const el = document.getElementById('chart-'+id);
        if(!el) return;
        el.classList.toggle('fullscreen');
        document.body.classList.toggle('no-scroll', el.classList.contains('fullscreen'));
        const cfg = charts.find(c => c.id === id);
        if(cfg) renderChart(cfg);
    }

    function fetchData(cb){
        showLoader();
        fetch('/dashboard/pivot-data/')
            .then(r => r.json())
            .then(data => { rawData = data; if(cb) cb(); })
            .finally(hideLoader);
    }

    function aggregate(metric){
        const grouped = {};
        rawData.forEach(row => {
            for(const [k,v] of Object.entries(filters)){
                if(k!==metric && v && row[k] !== v){
                    return;
                }
            }
            const key = row[metric] || '';
            grouped[key] = (grouped[key]||0)+1;
        });
        return Object.keys(grouped).map(k => ({label: k || 'N/A', value: grouped[k]}));
    }

    function colorScale(data){
        return d3.scaleOrdinal(d3.schemeCategory10).domain(data.map(d=>d.label));
    }

    function renderChart(cfg){
        const container = d3.select('#chart-'+cfg.id);
        const loader = container.select('.chart-loading');
        loader.style('display','block');
        const svg = container.select('svg');
        const legendEl = container.select('.chart-legend');
        // Ensure the SVG has explicit dimensions; relying solely on CSS can
        // result in clientWidth/clientHeight returning 0 which prevents D3
        // from rendering any shapes. Fallback to a default size when the
        // computed dimensions are zero.
        let width = +svg.node().clientWidth;
        let height = +svg.node().clientHeight;
        if (!width || !height) {
            width = parseInt(svg.style('width')) || 400;
            height = parseInt(svg.style('height')) || 400;
            svg.attr('width', width).attr('height', height);
        }
        svg.selectAll('*').remove();
        legendEl.html('');

        const data = aggregate(cfg.metric);
        const color = colorScale(data);
        if(!tooltip){
            tooltip = d3.select('body').append('div').attr('class','tooltip').style('opacity',0);
        }

        if(cfg.type === 'bar'){
            const x = d3.scaleBand().range([0,width]).padding(0.1).domain(data.map(d=>d.label));
            const y = d3.scaleLinear().range([height,0]).domain([0,d3.max(data,d=>d.value)]);
            svg.append('g').attr('transform',`translate(0,${height})`).call(d3.axisBottom(x));
            svg.append('g').call(d3.axisLeft(y));
            svg.selectAll('.bar').data(data).enter().append('rect')
                .attr('class','bar')
                .attr('x',d=>x(d.label))
                .attr('y',d=>y(d.value))
                .attr('width',x.bandwidth())
                .attr('height',d=>height-y(d.value))
                .attr('fill',d=>color(d.label))
                .on('click',(_,d)=>{ toggleFilter(cfg.metric,d.label); })
                .on('mousemove',(event,d)=>{
                    tooltip.style('opacity',1).html(`${d.label}: ${d.value}`)
                        .style('left',event.pageX+10+'px').style('top',event.pageY-15+'px');
                })
                .on('mouseout',()=>tooltip.style('opacity',0));
        } else if(cfg.type === 'line'){
            const x = d3.scalePoint().range([0,width]).domain(data.map(d=>d.label));
            const y = d3.scaleLinear().range([height,0]).domain([0,d3.max(data,d=>d.value)]);
            const line = d3.line().x(d=>x(d.label)).y(d=>y(d.value));
            svg.append('g').attr('transform',`translate(0,${height})`).call(d3.axisBottom(x));
            svg.append('g').call(d3.axisLeft(y));
            svg.append('path').datum(data).attr('fill','none').attr('stroke','#428bca').attr('stroke-width',2).attr('d',line);
            svg.selectAll('circle').data(data).enter().append('circle')
                .attr('cx',d=>x(d.label)).attr('cy',d=>y(d.value)).attr('r',4)
                .attr('fill',d=>color(d.label))
                .on('click',(_,d)=>{ toggleFilter(cfg.metric,d.label); })
                .on('mousemove',(event,d)=>{
                    tooltip.style('opacity',1).html(`${d.label}: ${d.value}`)
                        .style('left',event.pageX+10+'px').style('top',event.pageY-15+'px');
                })
                .on('mouseout',()=>tooltip.style('opacity',0));
        } else if(cfg.type === 'pie'){
            const radius = Math.min(width,height)/2;
            const g = svg.append('g').attr('transform',`translate(${width/2},${height/2})`);
            const pie = d3.pie().value(d=>d.value);
            const path = d3.arc().outerRadius(radius-10).innerRadius(0);
            const arc = g.selectAll('.arc').data(pie(data)).enter().append('g').attr('class','arc');
            arc.append('path')
                .attr('d',path)
                .attr('fill',d=>color(d.data.label))
                .on('click',(_,d)=>{ toggleFilter(cfg.metric,d.data.label); })
                .on('mousemove',(event,d)=>{
                    tooltip.style('opacity',1).html(`${d.data.label}: ${d.data.value}`)
                        .style('left',event.pageX+10+'px').style('top',event.pageY-15+'px');
                })
                .on('mouseout',()=>tooltip.style('opacity',0));
            arc.append('text').attr('transform',d=>`translate(${path.centroid(d)})`)
                .attr('dy','0.35em').text(d=>d.data.label);
        }

        const legendItem = legendEl.selectAll('.legend-item').data(data).enter().append('div').attr('class','legend-item');
        legendItem.append('span').attr('class','legend-color').style('background-color',d=>color(d.label));
        legendItem.append('span').text(d=>d.label);
        loader.style('display','none');
    }

    function renderAll(){
        charts.forEach(cfg=>renderChart(cfg));
    }

    function toggleFilter(metric,value){
        if(filters[metric] === value){
            delete filters[metric];
        }else{
            filters[metric] = value;
        }
        renderAll();
        saveDashboard();
    }

    function addChart(){
        if(charts.length >= 10){
            showModal('Maximum 10 charts allowed');
            return;
        }
        const type = document.getElementById('chart-type').value;
        const metric = document.getElementById('mscc-data-type').value;
        const id = ++counter;
        charts.push({id,type,metric});
        const container = document.createElement('div');
        container.id = 'chart-'+id;
        container.className = 'chart-wrapper';
        container.innerHTML = '<div class="chart-loading">Loading...</div>'+
            '<button class="delete-chart btn btn-danger btn-sm" style="position:absolute;top:5px;right:5px;">Delete</button>'+
            '<button class="fullscreen-chart btn btn-secondary btn-sm" style="position:absolute;top:5px;right:80px;">Fullscreen</button>'+
            '<svg></svg><div class="chart-legend"></div>';
        container.querySelector('.delete-chart').addEventListener('click', function(){
            removeChart(id);
        });
        container.querySelector('.fullscreen-chart').addEventListener('click', function(){
            toggleFullscreen(id);
        });
        document.getElementById('charts-container').appendChild(container);
        renderAll();
        saveDashboard();
    }

    function removeChart(id){
        charts = charts.filter(c=>c.id !== id);
        const el = document.getElementById('chart-'+id);
        if(el) el.remove();
        saveDashboard();
    }

    function saveDashboard(){
        localStorage.setItem('dashboardConfig', JSON.stringify({charts,filters}));
    }

    function loadDashboard(){
        const conf = localStorage.getItem('dashboardConfig');
        if(conf){
            const obj = JSON.parse(conf);
            charts = obj.charts || [];
            filters = obj.filters || {};
            counter = charts.reduce((m,c)=>Math.max(m,c.id),0);
            const roundSelect = document.getElementById('filter-round');
            if(roundSelect){
                roundSelect.value = filters.round || '';
            }
            const container = document.getElementById('charts-container');
            container.innerHTML = '';
            charts.forEach(c=>{
                const div = document.createElement('div');
                div.id = 'chart-'+c.id;
                div.className = 'chart-wrapper';
                div.innerHTML = '<div class="chart-loading">Loading...</div>'+
                    '<button class="delete-chart btn btn-danger btn-sm" style="position:absolute;top:5px;right:5px;">Delete</button>'+
                    '<button class="fullscreen-chart btn btn-secondary btn-sm" style="position:absolute;top:5px;right:80px;">Fullscreen</button>'+
                    '<svg></svg><div class="chart-legend"></div>';
                div.querySelector('.delete-chart').addEventListener('click', function(){
                    removeChart(c.id);
                });
                div.querySelector('.fullscreen-chart').addEventListener('click', function(){
                    toggleFullscreen(c.id);
                });
                container.appendChild(div);
            });
        }
    }

    document.addEventListener('DOMContentLoaded', function(){
        document.getElementById('add-chart').addEventListener('click', addChart);
        document.getElementById('save-dashboard').addEventListener('click', saveDashboard);
        const roundSelect = document.getElementById('filter-round');
        if(roundSelect){
            roundSelect.addEventListener('change', function(){
                const val = this.value;
                if(val){
                    filters.round = val;
                }else{
                    delete filters.round;
                }
                renderAll();
                saveDashboard();
            });
        }
        document.addEventListener('keyup', function(e){
            if(e.key === 'Escape'){
                const el = document.querySelector('.chart-wrapper.fullscreen');
                if(el){
                    const id = parseInt(el.id.replace('chart-',''));
                    toggleFullscreen(id);
                }
            }
        });
        document.getElementById('load-mscc-data').addEventListener('click', loadMsccData);
        fetchData(function(){
            loadDashboard();
            renderAll();
        });
    });
})();
