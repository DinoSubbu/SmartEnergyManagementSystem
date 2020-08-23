import { Component, OnInit } from '@angular/core';
import { MatSnackBar } from '@angular/material';
import { HttpService } from '../services/http.service';
import { formatDate } from '@angular/common';

@Component({
  selector: 'app-energy-generation',
  templateUrl: './energy-generation.component.html',
  styleUrls: ['./energy-generation.component.scss']
})
export class EnergyGenerationComponent implements OnInit {
  private windForecastUrl: string = "windForecast";
  private solarForecastUrl: string = "solarForecast";

  public chartType: string = 'bar';

  public chartDatasets: Array<any>;

  public chartLabels: Array<any> = [
    'No data gathered.'
  ];

  public chartColors: Array<any> = [];

  public chartOptions: any = {
    responsive: true,
    scales: {
      xAxes: [{
        stacked: true
      }],
      yAxes: [
        {
          stacked: true,
          scaleLabel: {
            display: true,
            labelString: 'Power produced in W (forecast)'
          }
        }
      ]
    }
  };

  constructor(private snackbar: MatSnackBar, private http: HttpService) {

    let requestWind = this.http.makeGetRequest(this.windForecastUrl);
    let requestSolar = this.http.makeGetRequest(this.solarForecastUrl);
    this.requestData(requestSolar, requestWind);
  }

  private requestData(requestSolar, requestWind) {
    // solar data request
    requestSolar.subscribe(
      (data: any) => {
        let chartDatasetsTemp: any = {};
        let chartLabelsTemp: string[] = [];
        let solarExampleName: string;
        let solarNames: string[] = [];

        data.map((element, index) => {
          if (index == 0) {
            solarExampleName = element.solarpanel_name;
          }
          if (this.checkDate(element.timestamp)) {
            // generate labels
            if (solarExampleName == element.solarpanel_name) {
              let timestamp = element.timestamp;
              // cut the string to the hour, set starting cut to 11 if just the hour should be showed
              timestamp = timestamp.slice(0, 13) + "h";
              chartLabelsTemp.push(timestamp);
            }
            chartDatasetsTemp[element.solarpanel_name] = chartDatasetsTemp[element.solarpanel_name] || []
            chartDatasetsTemp[element.solarpanel_name].push(element.supply);
            if (!solarNames.includes(element.solarpanel_name)) {
              solarNames.push(element.solarpanel_name)
            }
          }
        });
     

        // wind data request
        requestWind.subscribe(
          (data: any) => {

            let windNames: string[] = [];
            data.map((element, index) => {
              if (this.checkDate(element.timestamp)) {
                chartDatasetsTemp[element.windturbine_name] = chartDatasetsTemp[element.windturbine_name] || []
                chartDatasetsTemp[element.windturbine_name].push(element.supply);
                if (!windNames.includes(element.windturbine_name)) {
                  windNames.push(element.windturbine_name)
                }
              }
            });
            // graph data
            this.chartColors = [];
            for (let name in solarNames) {
              this.addSolarColor();
            }
            for (let name in windNames) {
              this.addWindColor();
            }
            this.chartLabels = chartLabelsTemp;
            this.chartDatasets = []
            for (let name in chartDatasetsTemp) {
              this.chartDatasets.push({ data: chartDatasetsTemp[name], label: name });
            }

          },
          // error handling
          error => {
            console.log(error);
            this.snackbar.open('Could not get data.', '', {
              duration: 3000
            });

          }
        );
      },
      // error handling
      error => {
        console.log(error);
        this.snackbar.open('Could not get data.', '', {
          duration: 3000
        });

      }
    );
  }

  addSolarColor() {
    this.chartColors.push(
      {
        backgroundColor:
          'rgba(255, 235, 59, .4)',
        borderColor:
          'rgba(158, 150, 0, 1)',
        borderWidth: 2,
      }
    );

  }

  addWindColor() {
    this.chartColors.push(
      {
        backgroundColor:
          'rgba(83, 109, 254, .2)',
        borderColor:
          'rgba(83, 109, 254, 1)',
        borderWidth: 2,
      },
    );

  }

  checkDate(timestamp: string, offsetCurrentDay: number = 1) {
    // converts to given datetime format   
    let datetime = new Date();
    let timestampDate = new Date(timestamp);
    let resultDate = new Date(datetime)
    resultDate.setDate(resultDate.getDate() + offsetCurrentDay);
    return (resultDate.getDate() == timestampDate.getDate());
  }

  ngOnInit() {
  }

  public chartClicked(e: any): void { }
  public chartHovered(e: any): void { }


}
