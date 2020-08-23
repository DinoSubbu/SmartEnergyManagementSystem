import { Component, OnInit } from '@angular/core';
import { HttpService } from '../services/http.service';
import { MatSnackBar } from '@angular/material';

@Component({
  selector: 'app-schedule-variation',
  templateUrl: './schedule-variation.component.html',
  styleUrls: ['./schedule-variation.component.scss']
})
export class ScheduleVariationComponent implements OnInit {

  ngOnInit(): void {
  }


  private currentDate: Date;

  // request specific 
  private urlSchedule: string = "schedule";
  private urlSimulation: string = "simulationDemand";

  // chart specificc
  public chartType: string = 'line';

  public chartDatasets: Array<any>;

  public chartLabels: Array<any> = ["No data gathered."];


  public chartColors: Array<any>;

  public chartOptions: any = {
    responsive: true,
    scales: {
      yAxes: [{
        scaleLabel: {
          display: true,
          labelString: 'Energy exchanged in Wh (positive values are bought, negative values are sold to the main grid provider)',
        }
      }]
    },
  };


  public chartClicked(e: any): void {
  }
  public chartHovered(e: any): void {
  }

  constructor(private http: HttpService, private snackbar: MatSnackBar) {
    let requestSchedule = this.http.makeGetRequestAddCurrentTime(this.urlSchedule);
    let requestSim = this.http.makeGetRequestAddCurrentTime(this.urlSimulation);

    this.requestData(requestSchedule, requestSim);
  }

  requestData(requestSchedule, requestSim) {
    requestSim.subscribe(
      (data: any) => {
        console.log(data)
        // connection successfull, but empty array returned
        if (data.length == 0) {
          this.snackbar.open('No data in database.', '', {
            duration: 2000
          });
          return;
        }

        this.snackbar.open('Data gathered.', '', {
          duration: 2000
        });

        let exchangeListSim: number[] = [];
        for (let index in data) {
          exchangeListSim.push(-data[index].energy)
        }
        let chartDatasetTemp = { data: exchangeListSim, label: "Simulation Exchange" };

        requestSchedule.subscribe(
          (data: any) => {
            // connection successfull, but empty array returned
            if (data.length == 0) {
              this.snackbar.open('No data in database.', '', {
                duration: 2000
              });
              return;
            }

            this.snackbar.open('Data gathered.', '', {
              duration: 2000
            });

            console.log(data)
            this.chartLabels = [];
            let exchangeList: number[] = [];
            let exchangeOverall = data.schedule.exchange_with_main_grid
            for (let index in exchangeOverall) {
              let exchange = exchangeOverall[index];
              exchangeList.push(exchange);
              this.chartLabels.push(index);
            }
            this.chartDatasets = [];

            this.chartDatasets.push(
              chartDatasetTemp,
              { data: exchangeList, label: "Optimizer Exchange" }
            )
            let exchangeDiff = []
            for (let i in exchangeList) {
              exchangeDiff[i] = Math.round(exchangeList[i] - exchangeListSim[i]);
            }
            this.chartDatasets.push(
              { data: exchangeDiff, label: "Difference between schedule and simulation" }
            )

          },
          // error handling
          error => {
            console.log(error);
            this.snackbar.open('Could not get data.', '', {
              duration: 3000
            });

          });


      },
      // error handling
      error => {
        console.log(error);
        this.snackbar.open('Could not get data.', '', {
          duration: 3000
        });

      });

  }

  historicalData(event) {
    let value = event.value;
    if (!value) {
      return;
    }
    if (this.currentDate == value) {
      return;
    }
    this.currentDate = value;
    let requestSchedule = this.http.makeGetRequestSpecificDate(this.urlSchedule, value);
    let requestSim = this.http.makeGetRequestSpecificDate(this.urlSimulation, value);

    this.requestData(requestSchedule, requestSim);

  }

  historicalDataInput(event) {
    this.historicalData(event)

  }


}

