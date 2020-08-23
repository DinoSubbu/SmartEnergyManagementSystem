import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { HttpService } from '../services/http.service';
import { MatSnackBar } from '@angular/material';
import { formatDate } from '@angular/common';

class Price {
  timestamp: string;
  retrievalTime: string;
  price: number;
}
  

@Component({
  selector: 'app-day-ahead-prices',
  templateUrl: './day-ahead-prices.component.html',
  styleUrls: ['./day-ahead-prices.component.scss']
})
export class DayAheadPricesComponent implements OnInit {
  // chart attributes
  public chartType: string = 'line';
  public chartDatasets: Array<any> = [
    { data: [0], label: 'Day-Ahead Prices' }
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
          labelString: 'Energy Price in € / MWh'
        }
      }]
    },     
    responsive: true
  };

  private url: string = "day-ahead-prices";
  
  private dataGathered: boolean;


  constructor(private http: HttpService, private snackbar: MatSnackBar) {
    let request = this.http.makeGetRequest(this.url);

    request.subscribe(
      (data: Price[]) => {
        console.log(data)
        // connection successfull, but empty array returned
        if(data.length == 0) {
          snackbar.open('No price data in database yet.', '', {
            duration: 2000
          });
          return;
        }

        this.dataGathered = true;

        snackbar.open('Latest price data gathered.', '', {
          duration: 2000
        });
        
        let chartDatasetsTemp: number[] = [];
        let chartLabelsTemp: String[] = [];
        data.forEach(element => {
          chartDatasetsTemp.push(element.price); 
          let timestamp = element.timestamp;
          // cut the string to the hour, set starting cut to 11 if just the hour should be showed
          timestamp = timestamp.slice(0, 13) + "h"
          chartLabelsTemp.push(timestamp);
        });
        this.chartDatasets = [
          { data: chartDatasetsTemp, label: 'Day-Ahead Prices' }
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
