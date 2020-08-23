import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { MatSnackBar } from '@angular/material';
import { HttpService } from '../services/http.service';

@Component({
  selector: 'app-battery',
  templateUrl: './battery.component.html',
  styleUrls: ['./battery.component.scss']
})
export class BatteryComponent implements OnInit {
  ngOnInit(): void {
  }
  private url: string = "batteryLatest";

  private batteries: any[] = [];
  private currentBatteryValue = 40;
  private currentStatus = 0;

  public chartType: string = 'bar';

  public chartDatasets: Array<any> = [
    { data: [65], label: 'Current Status' },
  ];

  public chartLabels: Array<any>;

  public chartColors: Array<any>;

  public chartOptions: any = {
    responsive: true,
    scales: {
      yAxes: [{
        ticks: {
          beginAtZero: true
        }
      }]
    }
  };

  constructor(private snackbar: MatSnackBar, private http: HttpService) {
    let request = this.http.makeGetRequest(this.url);

    request.subscribe(
      (data: any) => {
        // connection successfull, but empty array returned
        if (data.length == 0) {
          snackbar.open('No price data for the next day in database yet.', '', {
            duration: 2000
          });
          return;
        }

        snackbar.open('Data gathered.', '', {
          duration: 2000
        });

        // reset variables
        this.batteries = [];
        this.chartColors = [{
          backgroundColor: [],
          borderColor: [],
          borderWidth: 2
        }];
        let chartDataTemp = [];
        let chartLabelsTemp = [];
        for (let index in data) {
          let battery = data[index];
          let chargingRate = battery["currentChargingRate"];
          let name = battery["battery_name"];
          let energyRelative = (battery["currentEnergy"] / battery["energyUpperBound"]) * 100;
          this.batteries.push({
            name: name,
            energyRelative: energyRelative,
          });
          chartDataTemp.push(chargingRate);
          chartLabelsTemp.push(name);
          // charging => green
          if (chargingRate >= 0) {
            this.chartColors[0].backgroundColor.push(
              "rgba(66, 244, 75, .2)"
            );
            this.chartColors[0].borderColor.push(
              "rgba(66, 244, 75, 1)"
            );

            // discharging => red
          } else {
            this.chartColors[0].backgroundColor.push(
              "rgba(244, 95, 66, .2)"
            );
            this.chartColors[0].borderColor.push(
              "rgba(244, 95, 66, 1)"
            );
          }
        }

        this.chartDatasets = [{ data: chartDataTemp, label: "Battery" }];
        this.chartLabels = chartLabelsTemp;





      },
      // error handling
      error => {
        console.log(error);
        snackbar.open('Could not get data.', '', {
          duration: 3000
        });

      });
  }

  public chartClicked(e: any): void { }
  public chartHovered(e: any): void { }


}


