(function () {
    'use strict';
    var trend = JSON.parse(document.getElementById('trend-data').textContent || '[]');
    var schools = JSON.parse(document.getElementById('school-data').textContent || '[]');
    var chart = document.getElementById('attendance-trend');
    var bars = document.getElementById('school-comparison');
    var escapeHtml = function (value) {
        var element = document.createElement('span');
        element.textContent = value;
        return element.innerHTML;
    };

    if (!trend.length) {
        chart.innerHTML = '<div class="empty-state">No attendance data for this period</div>';
    } else {
        var width = 700, height = 240, pad = 35;
        var x = function (i) { return pad + i * ((width - pad * 2) / Math.max(trend.length - 1, 1)); };
        var y = function (value) { return height - pad - (value / 100) * (height - pad * 2); };
        var points = trend.map(function (item, i) { return x(i) + ',' + y(item.rate); }).join(' ');
        var grid = [0, 25, 50, 75, 100].map(function (value) {
            return '<line class="grid" x1="' + pad + '" y1="' + y(value) + '" x2="' + (width - pad) + '" y2="' + y(value) + '"/><text x="2" y="' + (y(value) + 4) + '">' + value + '%</text>';
        }).join('');
        var labels = trend.map(function (item, i) { return '<text text-anchor="middle" x="' + x(i) + '" y="230">' + item.month + '</text>'; }).join('');
        var dots = trend.map(function (item, i) { return '<circle class="dot" cx="' + x(i) + '" cy="' + y(item.rate) + '" r="4"><title>' + item.month + ': ' + item.rate + '%</title></circle>'; }).join('');
        chart.innerHTML = '<svg viewBox="0 0 ' + width + ' ' + height + '" preserveAspectRatio="none"><defs><linearGradient id="trendGradient" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#16836f" stop-opacity=".2"/><stop offset="1" stop-color="#16836f" stop-opacity="0"/></linearGradient></defs>' + grid + '<polygon class="area" points="' + pad + ',' + (height - pad) + ' ' + points + ' ' + (width - pad) + ',' + (height - pad) + '"/><polyline class="line" points="' + points + '"/>' + dots + labels + '</svg>';
    }

    if (!schools.length) {
        bars.innerHTML = '<div class="empty-state">No school data for this period</div>';
    } else {
        bars.innerHTML = schools.map(function (item) {
            var schoolName = escapeHtml(item.school);
            return '<div class="school-bar"><div class="school-bar-head"><strong title="' + schoolName + '">' + schoolName + '</strong><span>' + item.rate + '%</span></div><div class="progress-track"><i style="width:' + item.rate + '%"></i></div><small>' + item.records + ' records</small></div>';
        }).join('');
    }
}());
