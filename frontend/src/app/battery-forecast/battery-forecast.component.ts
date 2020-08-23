import { Component, OnInit } from '@angular/core';
import { HttpService } from '../services/http.service';
import { formatDate } from '@angular/common';
import { MatSnackBar } from '@angular/material';

@Component({
  selector: 'app-battery-forecast',
  templateUrl: './battery-forecast.component.html',
  styleUrls: ['./battery-forecast.component.scss']
})
export class BatteryForecastComponent implements OnInit {
  ngOnInit(): void {
  }

  // batteries
  private batteries: string[] = [];
  private batteryStates: any = {};
  private batteryStatesColors: any = {};
  private currentBattery: string = "";
  // request specific 
  private url: string = "batteryForecast";
  private dataGathered: boolean = false;


  // chart specific
  public chartType: string = 'line';
  public batteryChartType: string = 'horizontalBar';

  public batteryChartOptions: any = {
    responsive: true,
    scales: {
      xAxes: [{
        label: "Duration",
        ticks: {
          beginAtZero: true,
          fontFamily: "'Open Sans Bold', sans-serif",
          fontSize: 11,
          max: 24,
        },
        stacked: true
      }],
      yAxes: [{
        ticks: {
          beginAtZero: true
        },
        gridLines: {
          display: false,
          color: "#fff",
          zeroLineColor: "#fff",
          zeroLineWidth: 0,

        },
        stacked: true,
      }]

    },
    legend: {
      display: false
    },
    maintainAspectRatio: false,
    tooltips: {
      callbacks: {
        // custom tooltip
        label: function (tooltipItem, chartData) {
          return chartData.datasets[tooltipItem.datasetIndex].label
        }
      }
    },
  }

  public chartDatasets: Array<any> = [
    { data: [0], label: 'No data gathered' },
  ];
  public batteryChartDatasets: Array<any> = [
    { data: [0], label: 'No data gathered' },
  ];

  public chartLabels: Array<any> = [];
  public batteryChartLabels: Array<any> = [];

  public chartColors: Array<any> = [];
  public batteryChartColors: Array<any> = []

  public chartOptions: any = {
    responsive: true,
    scales: {
      yAxes: [{
        ticks: {
          beginAtZero: true
        },
        scaleLabel: {
          display: true,
          labelString: 'Energy Level in W'
        }
      }]
    }
  }



  public chartClicked(e: any): void {
  }
  public chartHovered(e: any): void {
  }

  constructor(private http: HttpService, private snackbar: MatSnackBar) {
    let request = this.http.makeGetRequestAddTime(this.url);

    request.subscribe(
      (data: any) => {
        // connection successfull, but empty array returned
        if (data.length == 0) {
          snackbar.open('No data for today in database yet.', '', {
            duration: 2000
          });
          return;
        }
        this.dataGathered = true;

        snackbar.open('Data gathered for tomorrow.', '', {
          duration: 2000
        });

        // reset variables
        let batteries = data.schedule.batteries
        this.batteryChartDatasets = [];
        this.batteryChartColors = [];
        this.chartDatasets = [];
        this.batteries = [];
        this.batteryStates = {};
        this.batteryStatesColors = {};
        console.log(batteries)

        for (let batteryName in batteries) {
          if (batteries.hasOwnProperty(batteryName)) {
            this.batteries.push(batteryName)
            let battery = batteries[batteryName]
            this.batteryStates[batteryName] = []
            this.batteryStatesColors[batteryName] = []
            // battery charging / discharging chart
            for (let index in battery.state) {
              let state = battery.state[index]
              // first letter uppercase
              state = state.charAt(0).toUpperCase() + state.slice(1);

              this.batteryStates[batteryName].push({ data: [1], label: state })
              if (state == "Charging") {
                this.batteryStatesColors[batteryName].push(
                  {
                    backgroundColor: "rgba(66, 244, 75, .8)",
                  }
                )
              } else if (state == "Discharging") {
                this.batteryStatesColors[batteryName].push(
                  {
                    backgroundColor: "rgba(244, 95, 66, .8)",
                  }
                )

              } else {
                this.batteryStatesColors[batteryName].push(
                  {
                    backgroundColor: "rgba(83, 109, 254, .8)",
                  }
                )

              }
            }

            // battery energy level
            let energy = []
            let labels = []
            for (let index in battery.energy) {
              energy.push(battery.energy[index]);
              labels.push(index);
            }
            this.chartLabels = labels;
            this.chartDatasets.push({ data: energy, label: batteryName });
          }
        }

        this.currentBattery = this.batteries[0];
        this.changeBattery(this.currentBattery)

      },
      // error handling
      error => {
        console.log(error);
        snackbar.open('Could not get data for today.', '', {
          duration: 3000
        });
        this.dataGathered = false;

        let request = this.http.makeGetRequestAddCurrentTime(this.url);

        request.subscribe(
          (data: any) => {
            // connection successfull, but empty array returned
            if (data.length == 0) {
              snackbar.open('No data for today in database yet.', '', {
                duration: 2000
              });
              return;
            }
            this.dataGathered = true;

            snackbar.open('Data gathered for today.', '', {
              duration: 2000
            });

            // reset variables
            let batteries = data.schedule.batteries
            this.batteryChartDatasets = [];
            this.batteryChartColors = [];
            this.chartDatasets = [];
            this.batteries = [];
            this.batteryStates = {};
            this.batteryStatesColors = {};
            console.log(batteries)

            for (let batteryName in batteries) {
              if (batteries.hasOwnProperty(batteryName)) {
                this.batteries.push(batteryName)
                let battery = batteries[batteryName]
                this.batteryStates[batteryName] = []
                this.batteryStatesColors[batteryName] = []
                // battery charging / discharging chart
                for (let index in battery.state) {
                  let state = battery.state[index]
                  // first letter uppercase
                  state = state.charAt(0).toUpperCase() + state.slice(1);

                  this.batteryStates[batteryName].push({ data: [1], label: state })
                  if (state == "Charging") {
                    this.batteryStatesColors[batteryName].push(
                      {
                        backgroundColor: "rgba(66, 244, 75, .8)",
                      }
                    )
                  } else if (state == "Discharging") {
                    this.batteryStatesColors[batteryName].push(
                      {
                        backgroundColor: "rgba(244, 95, 66, .8)",
                      }
                    )

                  } else {
                    this.batteryStatesColors[batteryName].push(
                      {
                        backgroundColor: "rgba(83, 109, 254, .8)",
                      }
                    )

                  }
                }

                // battery energy level
                let energy = []
                let labels = []
                for (let index in battery.energy) {
                  energy.push(battery.energy[index]);
                  labels.push(index);
                }
                this.chartLabels = labels;
                this.chartDatasets.push({ data: energy, label: batteryName });
              }
            }

            this.currentBattery = this.batteries[0];
            this.changeBattery(this.currentBattery)

          },
          // error handling
          error => {
            console.log(error);
            snackbar.open('Could not get data for tomorrow.', '', {
              duration: 3000
            });
            this.dataGathered = false;

          });

      });

  }

  changeBattery(value: string) {
    this.batteryChartColors = this.batteryStatesColors[value];
    this.batteryChartDatasets = this.batteryStates[value];
    this.batteryChartLabels = [value]
  }
}
