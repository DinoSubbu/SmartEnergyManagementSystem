import { Component, OnInit } from '@angular/core';
import { HttpService } from '../services/http.service';
import { MatSnackBar } from '@angular/material';

@Component({
  selector: 'app-current',
  templateUrl: './current.component.html',
  styleUrls: ['./current.component.scss']
})
export class CurrentComponent implements OnInit {
  ngOnInit(): void {
  }

  // request specific 
  private urls: string[] = [
    "solarLatest", "windLatest", "demandLatest", "batteryLatest"
  ]

  private names: string[] = [
    "solarpanel_name", "windturbine_name", "building_name", "battery_name"
  ]
  private labelNames: string[] = [
    "Solar Panel", "Wind Turbine", "Building", "Battery"
  ]
  private valueName: string[] = [
    "supply", "supply", "demand", "currentChargingRate"
  ]

  // chart specific
  public chartType: string = 'bar';

  public chartDatasets: Array<any> = [{
    data: ["0"], label: "No data gathered."
  }];;

  public chartLabels: Array<any>;

  public chartColors: Array<any> = [];

  public chartOptions: any = {
    responsive: true,
  }

  public chartDatasetsTemp: Array<any>;

  public chartColorsTemp: Array<any>;

  private numberOfEntities: number = 0;

  public chartClicked(e: any): void {
  }
  public chartHovered(e: any): void {
  }

  constructor(private http: HttpService, private snackbar: MatSnackBar) {
    for (let i = 0; i < 4; i++) {
      let request = this.http.makeGetRequest(this.urls[i]);
      request.subscribe(
        (data: any) => {
          // connection successfull, but empty array returned
          if (data.length == 0) {
            snackbar.open('No data in database.', '', {
              duration: 2000
            });
            return;
          }
          snackbar.open('Data gathered.', '', {
            duration: 2000
          });
          data.map((element, index) => {
            let name = element[this.names[i]];
            let value = element[this.valueName[i]];

            // buildings consume power
            if (i == 2) {
              value = -value;
            }

            // battery values need to be inverted to fit the graph meaning
            if (i == 3) {
              value = - value;
            }

            if (this.chartColorsTemp == undefined) {
              this.chartColorsTemp = [];
            }

            this.addColor(i);
            if (!this.chartDatasetsTemp || this.chartDatasetsTemp == undefined) {
              this.chartDatasetsTemp = [
                { data: [value], label: name }
              ]
            } else {
              this.chartDatasetsTemp.push({ data: [value], label: name });
            }


          });
          this.numberOfEntities++;

          if (this.numberOfEntities == 4) {
            this.chartLabels = ["Power produced/consumed in W"];
            this.chartColors = this.chartColorsTemp;
            this.chartDatasets = this.chartDatasetsTemp;
          }

        },
        // error handling
        error => {
          console.log(error);
          snackbar.open('Could not get data.', '', {
            duration: 3000
          });
        });

    }

  }

  private addColor(i: number) {
    let color: any;
    if (i == 0) {
      color = {
        backgroundColor:
          'rgba(255, 235, 59, .4)',
        borderColor:
          'rgba(158, 150, 0, 1)',
        borderWidth: 2,
      }
    } else if (i == 1) {
      color = {
        backgroundColor:
          'rgba(83, 109, 254, .4)',
        borderColor:
          'rgba(83, 109, 254, 1)',
        borderWidth: 2,
      }

    } else if (i == 2) {
      color = {
        backgroundColor:
          'rgba(255, 99, 132, 0.4)',
        borderColor:
          'rgba(255, 99, 132, 1)',
        borderWidth: 2,
      }

    } else if (i == 3) {
      color = {
        backgroundColor:
          'rgba(75, 192, 192, 0.4)',
        borderColor:
          'rgba(75, 192, 192, 1)',
        borderWidth: 2,
      }
    }
    this.chartColorsTemp.push(color);

  }
}
