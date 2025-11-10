   var data = {
       2020: [
           ['Lebanese', 1256916],
           ['Syrians', 804000],
           ['PRL', 68580],
           ['PRS', 10138],
       ],
   };

   var countries = [{
       name: 'Lebanese',
       color: 'rgba(255, 152, 0,0.4)',
       borderColor:'#074650'
   }, {
       name: 'Syrians',
       color: 'rgba(0, 162, 255,0.4)',
       borderColor: '#009292'
   }, {
       name: 'PRL',
       color: 'rgba(163, 102, 188,0.4)',
       borderColor: '#FE6DB6'
   }, {
       name: 'PRS',
       color: 'rgba(158, 229, 161,0.4)',
       borderColor: '#FEB5DA'
   }];

   function getData(data) {
       return data.map(function (country, i) {
           return {
               name: country[0],
               y: country[1],
               color: countries[i].color,
               borderColor: countries[i].borderColor
           };
       });
   }

   function getRandomNumber(){
        return Math.floor((Math.random() * 100) + 1);
   }

   Highcharts.theme = {
           colors: ['#074650', '#009292', '#FE6DB6', '#FEB5DA', '#480091', '#B66DFF'],
           title: {
               style: {
                   color: '#4D4D4D',
                   fontFamily: '"Poppins"',
                   fontSize:'18px',
                   fontWeight:'300',
               }
           },
           subtitle: {
               style: {
                   color: '#6A707E',
                   fontFamily: '"Poppins"',
                   fontSize:'13px',
                   fontWeight:'100',
               }
           },
           yAxis: {
               labels: {
                       style: {
                           color: '#525252',
                           fontFamily: '"Poppins"',
                           fontSize:'12px',
                           fontWeight:'100',
                       }
                   }
           },
           xAxis: {
               labels: {
                       style: {
                           color: '#525252',
                           fontFamily: '"Poppins"',
                           fontSize:'12px',
                           fontWeight:'100',
                       }
                   },
           },
           legend: {
               itemStyle: {
                   fontFamily: '"Poppins"',
                   fontSize:'13px',
                   fontWeight:'100',
                   color: '#ABAFB3'
               },
               itemHoverStyle:{
                   color: 'gray'
               },
               itemMarginTop: 10,
           },
           tooltip:{
               style: {
                   color: '#ABAFB3',
                   fontFamily: '"Poppins"',
                   fontSize:'12px',
                   fontWeight:'400',
               }
           },
           drilldown: {
               activeAxisLabelStyle: {
                   color: '#525252',
                   textDecoration:'none',
                   fontWeight:'100',
               },
               activeDataLabelStyle: {
                   color: '#ABAFB3',
                   display:'none'
               }
           },
           credits: {
    enabled: false
},
       };

   Highcharts.setOptions(Highcharts.theme);

   var children_per_gender_data = [{
               name: 'Male',
               y: 344,
               color: '#01B8AA'
           }, {
               name: 'Female',
               y: 434,
               color: '#FD625E'
           }];
   var children_cash_support_data = [{
               name: 'Haddi',
               y: 123,
               color: '#F17925'
           }, {
               name: 'Education Cash assistance',
               y: 2345,
               color: '#004753'
           }, {
               name: 'UNHCR cash assistance',
               y: 565,
               color: '#CCAA14'
           },{
               name: 'WFP cash assistance',
               y: 245,
               color: '#4B4C4E'
           }];

   var children_per_status_data = [{
               name: 'Married',
               y: 123,
               color: '#73B761'
           }, {
               name: 'Engaged',
               y: 2345,
               color: '#4A588A'
           }, {
               name: 'Divorced',
               y: 5,
               color: '#ECC846'
           },{
               name: 'Widowed',
               y: 0,
               color: '#CD4C46'
           },{
               name: 'Single',
               y: 1345,
               color: '#71AFE2'
           }];

    var children_per_programme_data = [{
                           name: "YBLN Level 1",
                           y: 233,
                           drilldown: "",
                           color: '#B66DFF'
                       },
                       {
                           name: "YBLN Level 2",
                           y: 234,
                           drilldown: "",
                           color: '#480091'
                       },
                       {
                           name: "YFS Level 1",
                           y: 343,
                           drilldown: "",
                           color: '#FE6DB6'
                       },
                       {
                           name: "YFS Level 2",
                           y: 343,
                           drilldown: "",
                           color: '#FE6DB6'
                       }];
    var children_per_nationality_data = [
                   {
                       name: "Lebanese",
                       y: 3864296,
                       drilldown: "Lebanese",
                       color: '#DC5B57',
                       borderColor:'#DC5B57'
                   },
                   {
                       name: "Syrian",
                       y: 1500000,
                       drilldown: "Syrian",
                       color: '#F3C911',
                       borderColor: '#F3C911'
                   },
                   {
                       name: "PRL",
                       y: 180000,
                       drilldown: "PRL",
                       color: '#4C5D8A',
                       borderColor: '#4C5D8A'
                   },
                   {
                       name: "PRS",
                       y: 27700,
                       drilldown: "PRS",
                       color: '#4A8DDC',
                       borderColor: '#4A8DDC'
                   }
               ];
    var children_per_nationality_data_drilldown = [
               {
                   name: "Lebanese",
                   id: "Lebanese",
                   data: [
                       [
                           "Under 1 year",
                           72758
                       ],
                       [
                           "Under 2 years",
                           171937
                       ],
                       [
                           "Under 5 years",
                           499339
                       ],
                       [
                           "3-5 years",
                           357407
                       ],
                       [
                           "6-14 years",
                           1218975
                       ],
                       [
                           "6-11 years",
                           770825
                       ],
                       [
                           "15-18 years",
                           477349
                       ],
                       [
                           "3-18 years",
                           1973031
                       ],
                       [
                           "0-5 years",
                           639012
                       ],
                       [
                           "0-17 years",
                           2135887
                       ],
                       [
                           "12-14 years",
                           367448
                       ],
                       [
                           "12-17 years",
                           726045
                       ],
                       [
                           "15-17 years",
                           358193
                       ],
                       [
                           "10-14 years",
                           622504
                       ]
                   ]
               },
               {
                   name: "Syrian",
                   id: "Syrian",
                   data: [
                       [
                           "Under 1 year",
                           30255
                       ],
                       [
                           "Under 2 years",
                           84544
                       ],
                       [
                           "Under 5 years",
                           257412
                       ],
                       [
                           "3-5 years",
                           167743
                       ],
                       [
                           "6-14 years",
                           401348
                       ],
                       [
                           "6-11 years",
                           293300
                       ],
                       [
                           "15-18 years",
                           118569
                       ],
                       [
                           "3-18 years",
                           687661
                       ],
                       [
                           "0-5 years",
                           312116
                       ],
                       [
                           "0-17 years",
                           805199
                       ],
                       [
                           "12-14 years",
                           108047
                       ],
                       [
                           "12-17 years",
                           199779
                       ],
                       [
                           "15-17 years",
                           91732
                       ],
                       [
                           "10-14 years",
                           197362
                       ]
                   ]
               },
               {
                   name: "PRL",
                   id: "PRL",
                   data: [
                       [
                           "Under 1 year",
                           3240
                       ],
                       [
                           "Under 2 years",
                           6689
                       ],
                       [
                           "Under 5 years",
                           17386
                       ],
                       [
                           "3-5 years",
                           10768
                       ],
                       [
                           "6-14 years",
                           30824
                       ],
                       [
                           "6-11 years",
                           20578
                       ],
                       [
                           "15-18 years",
                           14231
                       ],
                       [
                           "3-18 years",
                           55824
                       ],
                       [
                           "0-5 years",
                           21041
                       ],
                       [
                           "0-17 years",
                           62601
                       ],
                       [
                           "12-14 years",
                           10247
                       ],
                       [
                           "12-17 years",
                           20982
                       ],
                       [
                           "15-17 years",
                           10736
                       ],
                       [
                           "10-14 years",
                           16772
                       ]
                   ]
               },
               {
                   name: "PRS",
                   id: "PRS",
                   data: [
                       [
                           "Under 1 year",
                           527
                       ],
                       [
                           "Under 2 years",
                           1214
                       ],
                       [
                           "Under 5 years",
                           3017
                       ],
                       [
                           "3-5 years",
                           1758
                       ],
                       [
                           "6-14 years",
                           6022
                       ],
                       [
                           "6-11 years",
                           4216
                       ],
                       [
                           "15-18 years",
                           1973
                       ],
                       [
                           "3-18 years",
                           9753
                       ],
                       [
                           "0-5 years",
                           3631
                       ],
                       [
                           "0-17 years",
                           11172
                       ],
                       [
                           "12-14 years",
                           1806
                       ],
                       [
                           "12-17 years",
                           3325
                       ],
                       [
                           "15-17 years",
                           1518
                       ],
                       [
                           "10-14 years",
                           3252
                       ]
                   ]
               }
           ];
    var children_per_source_data = [{
                       name: "Dirassa",
                       y: 233,
                       drilldown: "",
                       color: '#01B8AA'
                   },
                   {
                       name: "Awareness Session",
                       y: 234,
                       drilldown: "",
                       color: '#374649'
                   },
                   {
                       name: "Sector Partners referral",
                       y: 233,
                       drilldown: "",
                       color: '#FD625E'
                   },
                   {
                       name: "From Profiling Database",
                       y: 343,
                       drilldown: "",
                       color: '#F2C80F'
                   },
                   {
                       name: "From Other NGO",
                       y: 545,
                       drilldown: "",
                       color: '#5F6B6D'
                   },
                   {
                       name: "From Displaced Community",
                       y: 767,
                       drilldown: "",
                       color: '#8AD4EB'
                   },
                   {
                       name: "Referred by the municipality",
                       y: 767,
                       drilldown: "",
                       color: '#FE9666'
                   },
                   {
                       name: "Other Sources",
                       y: 767,
                       drilldown: "",
                       color: '#A66999'
                   }];

    var children_per_disability_data = [{
                       name: "Walking",
                       y: 233,
                       color: '#01B8AA'
                   },
                   {
                       name: "Seeing",
                       y: 234,
                       color: '#374649'
                   },
                   {
                       name: "Hearing",
                       y: 233,
                       color: '#FD625E'
                   },
                   {
                       name: "Speaking",
                       y: 343,
                       color: '#F2C80F'
                   },
                   {
                       name: "Self Care",
                       y: 545,
                       color: '#5F6B6D'
                   },
                   {
                       name: "Learning",
                       y: 767,
                       color: '#8AD4EB'
                   },
                   {
                       name: "Interacting",
                       y: 767,
                       color: '#FE9666'
                   },
                   {
                       name: "Other",
                       y: 767,
                       color: '#A66999'
                   }];

    var children_per_vulnerability_data = [{
                           name: "Clear signs of neglect",
                           y: 69,
                           drilldown: "",
                           color: '#01B8AA'
                       },
                       {
                           name: "Clear signs of distress",
                           y: 424,
                           drilldown: "",
                           color: '#FD625E'
                       },
                       {
                           name: "Clear signs of physical maltreatment",
                           y: 123,
                           drilldown: "",
                           color: '#F2C80F'
                       }];

    var children_volunteering_data = [{
                           name: "Outreach",
                           y: 233,
                           drilldown: "",
                           color: '#01B8AA'
                       },
                       {
                           name: "Data entry",
                           y: 424,
                           drilldown: "",
                           color: '#FD625E'
                       },
                       {
                           name: "Admin work",
                           y: 123,
                           drilldown: "",
                           color: '#F2C80F'
                       },
                       {
                           name: "Empowerment and leadership",
                           y: 123,
                           drilldown: "",
                           color: '#8AD4EB'
                       },
                       {
                           name: "Awareness raising sessions",
                           y: 123,
                           drilldown: "",
                           color: '#FE9666'
                       },
                       {
                           name: "Other",
                           y: 123,
                           drilldown: "",
                           color: '#A66999'
                       }];

   var children_per_gender = create_pie_chart('children_per_gender', 'Gender', children_per_gender_data);
   var children_cash_support = create_pie_chart('children_cash_support', 'Support type', children_cash_support_data);
   var children_per_status = create_pie_chart('children_per_status', 'Support type', children_per_status_data);

   var children_per_programme = create_bar_chart('children_per_programme', children_per_programme_data, [])
   var children_per_nationality = create_bar_chart('children_per_nationality', children_per_nationality_data, children_per_nationality_data_drilldown)
   var children_per_source = create_bar_chart('children_per_source', children_per_source_data, [])
   var children_per_disability = create_pie_chart('children_per_disability', 'Disability', children_per_disability_data)
   var children_per_vulnerability = create_bar_chart('children_per_vulnerability', children_per_vulnerability_data, [])
   var children_volunteering = create_bar_chart('children_volunteering', children_volunteering_data, [])

   function create_pie_chart(container, series_name, data) {

       return Highcharts.chart(container, {
           chart: {
               plotBackgroundColor: null,
               plotBorderWidth: 0,
               plotShadow: false,
               type: 'pie'
           },
           title: {
               text: '',
               align: 'center',
               verticalAlign: 'middle',
               y: 50
           },
           subtitle: {
               text: '',
               align: 'left',
               verticalAlign: 'bottom',
           },
           tooltip: {
               pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
           },
           accessibility: {
               point: {
                   valueSuffix: '%'
               }
           },
           plotOptions: {
               pie: {
                   allowPointSelect: true,
                   cursor: 'pointer',
                   dataLabels: {
                       enabled: false,
                       format: '<b>{point.name}</b>: {point.percentage:.1f} %'
                   },
                   showInLegend: true
               },
                series: {
                    point: {
                        events: {
                            click: function () {
                                reload_dashboard_data(container);
                            }
                        }
                    }
                }
           },
           legend: {
               align: 'right',
               verticalAlign: 'middle',
               layout: 'vertical',

           },
           series: [{
               name: series_name,
               colorByPoint: true,
               innerSize: '50%',
               data: data
           }]
       });
    }

   function create_bar_chart(container, data, drilldown) {

       return Highcharts.chart(container, {
           chart: {
               type: 'column',
                 margin:80,
               marginBottom:100,

           },
           title: {
               text: '',

           },
           subtitle: {
               text: '',
               align: 'left',
               verticalAlign: 'bottom',
           },
           accessibility: {
               announceNewData: {
                   enabled: true
               }
           },
           xAxis: {
               type: 'category'
           },
           yAxis: {
               title: {
                   text:' '
               }

           },
           legend: {
               enabled: false
           },
           plotOptions: {
               series: {
                   borderWidth: 1,
                   borderColor:'{point.borderColor}',
                   pointWidth:40,
                   dataLabels: {
                       enabled: false,
                       formatter: function() {
                         return formatNumber(this.point.y);
                       }
                   },
                    point: {
                        events: {
                            click: function () {
                                reload_dashboard_data(container);
                            }
                        }
                    }
               }
           },

           tooltip: {
               formatter: function() {
                     return '<b>'+this.point.name+': </b>'+ formatNumber(this.point.y);
               }
           },

           series: [
               {
                   name: "",
                   colorByPoint: true,
                   data: data,
               }
           ],
           drilldown: {
               series: drilldown
           }
       });
   }


$(document).on('click',  '.filter-package-type', function(){

    $('.filter-package-type').removeClass('bg-light');
    $(this).addClass('bg-light');

    reload_dashboard_data();
});

function reload_dashboard_data(exclude_container){

    if(exclude_container != 'children_per_gender') {
        children_per_gender.update({
           series: [{
               data: generate_new_data(children_per_gender_data)
           }]
        });
    }

    if(exclude_container != 'children_cash_support') {
        children_cash_support.update({
           series: [{
               data: generate_new_data(children_cash_support_data)
           }]
        });
    }

    if(exclude_container != 'children_per_status') {
        children_per_status.update({
           series: [{
               data: generate_new_data(children_per_status_data)
           }]
        });
    }

    if(exclude_container != 'children_per_programme') {
        children_per_programme.update({
           series: [{
               data: generate_new_data(children_per_programme_data)
           }]
        });
    }

    if(exclude_container != 'children_per_nationality') {
        children_per_nationality.update({
           series: [{
               data: generate_new_data(children_per_nationality_data)
           }]
        });
    }

    if(exclude_container != 'children_per_source') {
        children_per_source.update({
           series: [{
               data: generate_new_data(children_per_source_data)
           }]
        });
    }

    if(exclude_container != 'children_per_disability') {
        children_per_disability.update({
           series: [{
               data: generate_new_data(children_per_disability_data)
           }]
        });
    }

    if(exclude_container != 'children_per_vulnerability') {
        children_per_vulnerability.update({
           series: [{
               data: generate_new_data(children_per_vulnerability_data)
           }]
        });
    }

    if(exclude_container != 'children_volunteering') {
        children_volunteering.update({
           series: [{
               data: generate_new_data(children_volunteering_data)
           }]
        });
    }
}

function generate_new_data(data){

    var new_data = []

    $(data).each(function(i, item){
        item['y'] = getRandomNumber();
        new_data[i] = item
    });

    return new_data;
}


function getPointCategoryName(point, dimension) {
    var series = point.series,
        isY = dimension === 'y',
        axis = series[isY ? 'yAxis' : 'xAxis'];
    return axis.categories[point[isY ? 'y' : 'x']];
}

Highcharts.chart('attendance', {

    chart: {
        type: 'heatmap',
        marginTop: 40,
        marginBottom: 80,
        plotBorderWidth: 1
    },


    title: {
        text: ''
    },

    xAxis: {
        categories: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    },

    yAxis: {
        categories: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
        title: null,
        reversed: true
    },

    accessibility: {
        point: {
            descriptionFormatter: function (point) {
                var ix = point.index + 1,
                    xName = getPointCategoryName(point, 'x'),
                    yName = getPointCategoryName(point, 'y'),
                    val = point.value;
                return ix + '. ' + xName + ' - ' + yName + ', ' + val + '.';
            }
        }
    },

    colorAxis: {
        min: 0,
        minColor: '#FFFFFF',
        maxColor: '#FD625E'
    },

    legend: {
        align: 'right',
        layout: 'vertical',
        margin: 0,
        verticalAlign: 'top',
        y: 25,
        symbolHeight: 280
    },

    tooltip: {
        formatter: function () {
            return '<b>' + getPointCategoryName(this.point, 'x') + '</b> <br><b>' +
                this.point.value + '</b> <br><b>' + getPointCategoryName(this.point, 'y') + '</b>';
        }
    },

    series: [{
        name: 'Attendances',
        borderWidth: 1,
        data: [
        [0, 0, 10], [0, 1, 19], [0, 2, 8], [0, 3, 24], [0, 4, 67],
        [1, 0, 92], [1, 1, 58], [1, 2, 78], [1, 3, 117], [1, 4, 48],
        [2, 0, 35], [2, 1, 15], [2, 2, 123], [2, 3, 64], [2, 4, 52],
        [3, 0, 72], [3, 1, 132], [3, 2, 114], [3, 3, 19], [3, 4, 16],
        [4, 0, 38], [4, 1, 5], [4, 2, 8], [4, 3, 117], [4, 4, 115],
        [5, 0, 88], [5, 1, 32], [5, 2, 12], [5, 3, 6], [5, 4, 120],
        [6, 0, 13], [6, 1, 44], [6, 2, 88], [6, 3, 98], [6, 4, 96],
        [7, 0, 31], [7, 1, 1], [7, 2, 82], [7, 3, 32], [7, 4, 30],
        [8, 0, 85], [8, 1, 97], [8, 2, 123], [8, 3, 64], [8, 4, 84],
        [9, 0, 47], [9, 1, 114], [9, 2, 31], [9, 3, 48], [9, 4, 91],
        [10, 0, 10], [10, 1, 19], [10, 2, 8], [10, 3, 24], [10, 4, 67],
        [11, 0, 92], [11, 1, 58], [11, 2, 78], [11, 3, 117], [11, 4, 48],
        ],
        dataLabels: {
            enabled: true,
            color: '#000000'
        }
    }],

    responsive: {
        rules: [{
            condition: {
                maxWidth: 500
            },
            chartOptions: {
                yAxis: {
                    labels: {
                        formatter: function () {
                            return this.value.charAt(0);
                        }
                    }
                }
            }
        }]
    }

});
