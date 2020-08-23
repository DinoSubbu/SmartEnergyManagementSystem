import { Component, OnInit } from '@angular/core';
import { HttpService } from '../services/http.service';
import { formatDate } from '@angular/common';
import { MatSnackBar } from '@angular/material';

@Component({
  selector: 'app-components',
  templateUrl: './components.component.html',
  styleUrls: ['./components.component.scss']
})
export class ComponentsComponent {
  // request specific 
  private url: string = "components";

  // building data
  private buildings: string[] = [];
  private currentBuilding: string = "";
  private buildingDataset: any = {};
  private buildingLabels: any = {};

  // chart specificc
  public chartType: string = 'horizontalBar';

  public chartDatasets: Array<any> = [
    { data: [0], label: 'No data gathered.' },
  ];

  public chartLabels: Array<any> = ["No data gathered."];

  public chartColors: Array<any> = [
    {
      backgroundColor: "rgba(63,103,126,0)",
      borderColor: "rgba(63,103,126,0)",
      borderWidth: 2,
      hoverBackgroundColor: "rgba(50,90,100,0)"
    },
    {
      backgroundColor: "rgba(83, 109, 254, .8)",
    }
  ];

  public chartOptions: any = {
    responsive: true,
    hover: {
      animationDuration: 10
    },
    tooltips: {
      custom: function (tooltipModel) {
        // hide the tooltip for invisible data
        // see https://github.com/chartjs/Chart.js/issues/1889 for more information
        if (!tooltipModel.body || tooltipModel.body.length < 1) {
          tooltipModel.caretSize = 0;
          tooltipModel.xPadding = 0;
          tooltipModel.yPadding = 0;
          tooltipModel.cornerRadius = 0;
          tooltipModel.width = 0;
          tooltipModel.height = 0;
        }
      },
      // Hide tooltip body
      filter: function (tooltipItem, chartData) {
        let show: boolean = tooltipItem.datasetIndex === 1;
        return show;
      },
      callbacks: {
        // custom tooltip
        label: function (tooltipItem, chartData) {
          return "  " + chartData.datasets[0].data[tooltipItem.index] + " - " + (parseInt(tooltipItem.xLabel) + chartData.datasets[0].data[tooltipItem.index]);
        }
      }
    },
    scales: {
      xAxes: [{
        label: "Duration",
        ticks: {
          beginAtZero: true,
          fontFamily: "'Open Sans Bold', sans-serif",
          fontSize: 11,
          max: 24
        },
        scaleLabel: {
          display: true,
          labelString: 'Time of operation for each component of a building'
        },
        stacked: true
      }],
      yAxes: [{
        gridLines: {
          display: false,
          color: "#fff",
          zeroLineColor: "#fff",
          zeroLineWidth: 0
        },
        stacked: true
      }]
    },
    legend: {
      display: false
    },
  };


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
          snackbar.open('No data for tomorrow in database yet.', '', {
            duration: 2000
          });
          return;
        }

        snackbar.open('Data gathered for tomorrow.', '', {
          duration: 2000
        });

        // component chart 
        console.log(data)
        let buildingsTemp = data.schedule.buildings
        this.chartDatasets = [];
        this.buildings = [];
        this.buildingDataset = {};
        this.buildingLabels = {};

        for (let buildingName in buildingsTemp) {
          this.buildings.push(buildingName)
          this.buildingLabels[buildingName] = [];
          this.buildingDataset[buildingName] = [];
          let building = buildingsTemp[buildingName];

          let startValues: number[] = []
          let endValues: number[] = []

          for (let componentName in building) {
            let component = building[componentName];
            this.buildingLabels[buildingName].push(componentName);
            let start = component["start"];
            let end = component["end"];

            startValues.push(start);
            endValues.push(end - start);

          }
          this.buildingDataset[buildingName].push(
            { data: startValues, label: 'start values' },
            { data: endValues, label: 'end values' }
          )
        }

        this.currentBuilding = this.buildings[0];
        this.changeBuilding(this.currentBuilding);
      },
      // error handling
      error => {
        console.log(error);
        snackbar.open('Could not get data for tomorrow.', '', {
          duration: 3000
        });

        let request = this.http.makeGetRequestAddCurrentTime(this.url);

        request.subscribe(
          (data: any) => {
            // connection successfull, but empty array returned
            if (data.length == 0) {
              snackbar.open('No data for the next day in database yet.', '', {
                duration: 2000
              });
              return;
            }

            snackbar.open('Data gathered for today.', '', {
              duration: 2000
            });

            // component chart 
            console.log(data)
            let buildingsTemp = data.schedule.buildings
            this.chartDatasets = [];
            this.buildings = [];
            this.buildingDataset = {};
            this.buildingLabels = {};

            for (let buildingName in buildingsTemp) {
              this.buildings.push(buildingName)
              this.buildingLabels[buildingName] = [];
              this.buildingDataset[buildingName] = [];
              let building = buildingsTemp[buildingName];

              let startValues: number[] = []
              let endValues: number[] = []

              for (let componentName in building) {
                let component = building[componentName];
                this.buildingLabels[buildingName].push(componentName);
                let start = component["start"];
                let end = component["end"];

                startValues.push(start);
                endValues.push(end - start);

              }
              this.buildingDataset[buildingName].push(
                { data: startValues, label: 'start values' },
                { data: endValues, label: 'end values' }
              )
            }

            this.currentBuilding = this.buildings[0];
            this.changeBuilding(this.currentBuilding);
          },
          // error handling
          error => {
            console.log(error);
            snackbar.open('Could not get data for today.', '', {
              duration: 3000
            });

          });

      });

  }

  changeBuilding(value) {
    this.chartDatasets = this.buildingDataset[value];
    this.chartLabels = this.buildingLabels[value];
  }
}
