import { Component, OnInit } from '@angular/core';
import { HttpService } from '../services/http.service';
import { formatDate } from '@angular/common';
import { MatSnackBar } from '@angular/material';

@Component({
  selector: 'app-schedule',
  templateUrl: './schedule.component.html',
  styleUrls: ['./schedule.component.scss']
})
export class ScheduleComponent implements OnInit {
  ngOnInit(): void {
  }

  // request specific 
  private url: string = "schedule";

  // chart specificc
  public chartType: string = 'line';

  public chartDatasets: Array<any> = [
    { data: [0], label: 'No data gathered.' },
  ];

  public chartLabels: Array<any> = ["No data gathered."];


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
          labelString: 'Energy exchanged in Wh (positive values are bought, negative values are sold to the main grid provider)',
        }
      }]
    },
    responsive: true
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
          snackbar.open('No schedule data for the next day in database yet.', '', {
            duration: 2000
          });
          return;
        }

        snackbar.open('Schedule for tomorrow gathered.', '', {
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

        this.chartDatasets = [
          { data: exchangeList, label: "Exchange" }
        ]


      },
      // error handling
      error => {
        console.log(error);
        snackbar.open('No schedule data for the next day in database yet.', '', {
          duration: 3000
        });

        let request = this.http.makeGetRequestAddCurrentTime(this.url);

        request.subscribe(
          (data: any) => {
            // connection successfull, but empty array returned
            if (data.length == 0) {
              snackbar.open('No schedule data for the next day in database yet.', '', {
                duration: 2000
              });
              return;
            }

            snackbar.open('Schedule for today gathered.', '', {
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

            this.chartDatasets = [
              { data: exchangeList, label: "Exchange" }
            ]


          },
          // error handling
          error => {
            console.log(error);
            snackbar.open('Could not get data.', '', {
              duration: 3000
            });

          });


      });

  }

}

