class Template:
    def __init__(self, chart_filter: list = None):
        self.charts = {
            1: "var chart1 = new Chart(document.getElementById('chart1'), config1);",
            2: "var chart2 = new Chart(document.getElementById('chart2'), config2);",
            3: "var chart3 = new Chart(document.getElementById('chart3'), config3);",
            4: "var chart4 = new Chart(document.getElementById('chart4'), config4);",
            5: "var chart5 = new Chart(document.getElementById('chart5'), config5);",
            6: "var chart6 = new Chart(document.getElementById('chart6'), config6);"
        }
        self.table = """
            <tr>
                <td>{pool}</td>
                <td>{pity}</td>
                <td>{name}</td>
                <td>{date}</td>
            </tr>
        """

        if chart_filter is not None:
            for i in chart_filter:
                del self.charts[i]

    def __call__(self, params: dict, table_data: list) -> str:
        html_part1 = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>分析結果</title>
                <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
                <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;700&display=swap" rel="stylesheet">
                <style>
                    body {{
                        background-image: url('bg.png');
                        background-size: cover;
                        background-position: center center;
                        color: #000000;
                        font-family: 'Noto Sans TC', sans-serif;
                        margin: 0;
                        padding: 0;
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                    }}
                    .content-container {{
                        width: 100%;
                        max-width: 1200px;
                        margin: 20px auto;
                    }}
                    .header-container {{
                        display: flex;
                        justify-content: space-between;
                        padding: 10px;
                        gap: 20px;
                        width: 100%;
                    }}
                    .header-container-box {{
                        flex: 1;
                        background-color: rgba(255, 255, 255, 0.9);
                        color: #000000;
                        padding: 20px;
                        border-radius: 10px;
                        text-align: center;
                        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                    }}
                    .chart-container {{
                        background-color: rgba(255, 255, 255, 0.9);
                        width: 100%;
                        border-radius: 15px;
                        padding: 20px;
                        margin-top: 20px;
                        display: flex;
                        flex-wrap: wrap;
                        justify-content: space-between;
                        gap: 20px;
                        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                    }}
                    .chart-item {{
                        flex: 1;
                        max-width: 300px;
                        transition: transform 0.3s;
                    }}
                    .chart-item:hover {{
                        transform: scale(1.05);
                    }}
                    .other-container {{
                        background-color: rgba(255, 255, 255, 0.9);
                        border-radius: 15px;
                        padding: 20px;
                        margin-top: 20px;
                        width: 100%;
                        display: flex;
                        justify-content: space-around;
                        flex-wrap: wrap;
                        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                    }}
                    .item {{
                        background-color: rgba(255, 255, 255, 0.9);
                        color: #000000;
                        border-radius: 10px;
                        padding: 15px;
                        margin: 5px;
                        width: 200px;
                        text-align: center;
                        transition: transform 0.3s;
                        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                    }}
                    .item:hover {{
                        transform: scale(1.05);
                    }}
                    .item-row {{
                        margin-top: 10px;
                    }}
                    .table-container {{
                        max-height: 400px; /* 設置最大高度 */
                        overflow: auto;
                        background-color: rgba(255, 255, 255, 0.9);
                        border-radius: 15px;
                        padding: 20px;
                        margin-top: 20px;
                        width: 100%;
                        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                        transition: transform 0.3s;
                    }}
                    .table-container:hover {{
                        transform: scale(1.02);
                    }}
                    table {{
                        width: 100%;
                        border-collapse: collapse;
                    }}
                    th, td {{
                        border: 1px solid #ddd;
                        padding: 10px;
                        text-align: center;
                    }}
                    th {{
                        background-color: #f2f2f2;
                    }}
                    tr:hover {{
                        background-color: #f5f5f5;
                    }}
                </style>
            </head>
            <body>
                <div class="content-container">
                    <div class="header-container">
                        <div class="header-container-box">
                            <p style="text-align: center; font-size: 50px;"><b>運氣評分:{params["運氣分數"]}({params["評級"]})</b></p>
                        </div>
                        <div class="header-container-box">
                            <p style="text-align: left; font-size: 30px; padding-left: 20px"><b>總抽數:{params["總抽數"]}</b></p>
                            <p style="text-align: left; font-size: 30px; padding-left: 20px"><b>五星數:{params["五星數"]}</b></p>
                            <p style="text-align: left; font-size: 30px; padding-left: 20px"><b>平均出金:{params["總抽數"]//params["五星數"]}</b></p>
                        </div>
                    </div>
                    <div class="chart-container">
                        <div class="chart-item"><canvas id="chart1"></canvas></div>
                        <div class="chart-item"><canvas id="chart2"></canvas></div>
                        <div class="chart-item"><canvas id="chart3"></canvas></div>
                        <div class="chart-item"><canvas id="chart4"></canvas></div>
                        <div class="chart-item"><canvas id="chart5"></canvas></div>
                        <div class="chart-item"><canvas id="chart6"></canvas></div>
                    </div>
                    <div class="other-container">
                        <div class="item">
                            角色活動喚取(保底計數)
                            <div class="item-row">五星 {params["角色活動五星第"]}/80</div>
                            <div class="item-row">四星 {params["角色活動四星第"]}/10</div>
                            <div class="item-row">上一個五星:{params["角色活動上一個五星"]}</div>
                        </div>
                        <div class="item">
                            武器活動喚取(保底計數)
                            <div class="item-row">五星 {params["武器活動五星第"]}/80</div>
                            <div class="item-row">四星 {params["武器活動四星第"]}/10</div>
                            <div class="item-row">上一個五星:{params["武器活動上一個五星"]}</div>
                        </div>
                        <div class="item">
                            角色常駐喚取(保底計數)
                            <div class="item-row">五星 {params["角色常駐五星第"]}/80</div>
                            <div class="item-row">四星 {params["角色常駐四星第"]}/10</div>
                            <div class="item-row">上一個五星:{params["角色常駐上一個五星"]}</div>
                        </div>
                        <div class="item">
                            武器常駐喚取(保底計數)
                            <div class="item-row">五星 {params["武器常駐五星第"]}/80</div>
                            <div class="item-row">四星 {params["武器常駐四星第"]}/10</div>
                            <div class="item-row">上一個五星:{params["武器常駐上一個五星"]}</div>
                        </div>
                    </div>
                    <div class="table-container">
                        <h2>五星紀錄</h2>
                        <table>
                            <thead>
                                <tr>
                                    <th>卡池</th>
                                    <th>出貨抽數</th>
                                    <th>名稱</th>
                                    <th>日期</th>
                                </tr>
                            </thead>
                            <tbody>
                """
        html_part2 = f"""
                            </tbody>
                        </table>
                    </div>
                </div>
                <script>
                    const labels = ['5星', '4星', '3星'];

                    const data1 = {{
                        labels: labels,
                        datasets: [{{
                            label: '數量',
                            data: [{params["角色活動五星"]}, {params["角色活動四星"]}, {params["角色活動三星"]}],
                            backgroundColor: ['#FFD306', '#9393FF', '#97CBFF'],
                            hoverOffset: 4
                        }}]
                    }};

                    const data2 = {{
                        labels: labels,
                        datasets: [{{
                            label: '數量',
                            data: [{params["武器活動五星"]}, {params["武器活動四星"]}, {params["武器活動三星"]}],
                            backgroundColor: ['#FFD306', '#9393FF', '#97CBFF'],
                            hoverOffset: 4
                        }}]
                    }};

                    const data3 = {{
                        labels: labels,
                        datasets: [{{
                            label: '數量',
                            data: [{params["角色常駐五星"]}, {params["角色常駐四星"]}, {params["角色常駐三星"]}],
                            backgroundColor: ['#FFD306', '#9393FF', '#97CBFF'],
                            hoverOffset: 4
                        }}]
                    }};

                    const data4 = {{
                        labels: labels,
                        datasets: [{{
                            label: '數量',
                            data: [{params["武器常駐五星"]}, {params["武器常駐四星"]}, {params["武器常駐三星"]}],
                            backgroundColor: ['#FFD306', '#9393FF', '#97CBFF'],
                            hoverOffset: 4
                        }}]
                    }};

                    const data5 = {{
                        labels: labels,
                        datasets: [{{
                            label: '數量',
                            data: [{params["新手五星"]}, {params["新手四星"]}, {params["新手三星"]}],
                            backgroundColor: ['#FFD306', '#9393FF', '#97CBFF'],
                            hoverOffset: 4
                        }}]
                    }};

                    const data6 = {{
                        labels: labels,
                        datasets: [{{
                            label: '數量',
                            data: [{params["新手定向五星"]}, {params["新手定向四星"]}, {params["新手定向三星"]}],
                            backgroundColor: ['#FFD306', '#9393FF', '#97CBFF'],
                            hoverOffset: 4
                        }}]
                    }};

                    const config1 = {{
                        type: 'pie',
                        data: data1,
                        options: {{
                            responsive: true,
                            plugins: {{
                                legend: {{
                                    position: 'top',
                                }},
                                title: {{
                                    display: true,
                                    text: '角色活動喚取'
                                }}
                            }}
                        }},
                    }};

                    const config2 = {{
                        type: 'pie',
                        data: data2,
                        options: {{
                            responsive: true,
                            plugins: {{
                                legend: {{
                                    position: 'top',
                                }},
                                title: {{
                                    display: true,
                                    text: '武器活動喚取'
                                }}
                            }}
                        }},
                    }};

                    const config3 = {{
                        type: 'pie',
                        data: data3,
                        options: {{
                            responsive: true,
                            plugins: {{
                                legend: {{
                                    position: 'top',
                                }},
                                title: {{
                                    display: true,
                                    text: '角色常駐喚取'
                                }}
                            }}
                        }},
                    }};

                    const config4 = {{
                        type: 'pie',
                        data: data4,
                        options: {{
                            responsive: true,
                            plugins: {{
                                legend: {{
                                    position: 'top',
                                }},
                                title: {{
                                    display: true,
                                    text: '武器常駐喚取'
                                }}
                            }}
                        }},
                    }};

                    const config5 = {{
                        type: 'pie',
                        data: data5,
                        options: {{
                            responsive: true,
                            plugins: {{
                                legend: {{
                                    position: 'top',
                                }},
                                title: {{
                                    display: true,
                                    text: '新手喚取'
                                }}
                            }}
                        }},
                    }};

                    const config6 = {{
                        type: 'pie',
                        data: data6,
                        options: {{
                            responsive: true,
                            plugins: {{
                                legend: {{
                                    position: 'top',
                                }},
                                title: {{
                                    display: true,
                                    text: '新手自選喚取'
                                }}
                            }}
                        }},
                    }};
        """

        html_end = """
                </script>
            </body>
        </html>
        """

        if self.charts:
            for i in self.charts.values():
                html_part2 += "\n"
                html_part2 += i

        for item in table_data:
            html_part1 += "\n"
            html_part1 += self.table.format(pool=item[0], pity=item[3], name=item[1], date=item[2])

        html_part1 += "\n"
        html_part1 += html_part2
        html_part1 += "\n"
        html_part1 += html_end

        return html_part1
