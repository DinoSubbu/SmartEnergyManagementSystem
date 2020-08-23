import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { HttpService } from '../services/http.service';
import { MatSnackBar } from '@angular/material';
import { formatDate } from '@angular/common';

class Co2 {
  timestamp: string;
  carbonIntensity: number;
}

@Component({
  selector: 'app-co2-forecast-proxy',
  templateUrl: './co2-forecast-proxy.component.html',
  styleUrls: ['./co2-forecast-proxy.component.scss']
})
export class Co2ForecastProxyComponent implements OnInit {

  // chart attributes
  public chartType: string = 'line';
  public chartDatasets: Array<any> = [
    { data: [0], label: 'Co2 Emission Forecast' }
  ];
  public chartLabels: Array<any> = [
    'No data gathered.'
  ];
  public chartColors: Array<any> = [
    {
      backgroundColor: 'rgba(83, 109, 254, .2)',
      borderColor: 'rgba(83, 109, 254, .7)',
      borderWidth: 2,
    }
  ];
  public chartOptions: any = {
    scales: {
      yAxes: [{
        scaleLabel: {
          display: true,
          labelString: 'CO2 emission intensity in g CO2/KWh'
        }
      }]
    },     
    responsive: true
  };

  private url: string = "co2Forecast";
  
  private dataGathered: boolean;

  constructor(private http: HttpService, private snackbar: MatSnackBar) {
    let request = this.http.makeGetRequest(this.url);

    request.subscribe(
      (data: Co2[]) => {
        console.log(data)
        // connection successfull, but empty array returned
        if(data.length == 0) {
          snackbar.open('No Co2 emission data in database yet.', '', {
            duration: 2000
          });
          return;
        }

        this.dataGathered = true;

        snackbar.open('Latest co2 emission data gathered.', '', {
          duration: 2000
        });
        
        let chartDatasetsTemp: number[] = [];
        let chartLabelsTemp: String[] = [];
        data.forEach(element => {
          chartDatasetsTemp.push(element.carbonIntensity); 
          let timestamp = element.timestamp;
          // cut the string to the hour, set starting cut to 11 if just the hour should be showed
          //timestamp = timestamp.slice(0, 13) + "h"
          chartLabelsTemp.push(timestamp);
        });
        this.chartDatasets = [
          { data: chartDatasetsTemp, label: 'Co2-Emission-Forecast' }
        ];
        this.chartLabels = chartLabelsTemp;
      },
      // error handling
      error => {
        console.log(error);
        snackbar.open('Could not get data.', '', {
          duration: 3000
        });
        this.dataGathered = false;

      });
    
  }

  ngOnInit() {
  }

  public chartClicked(e: any): void {
  }
  public chartHovered(e: any): void {
  }
}
