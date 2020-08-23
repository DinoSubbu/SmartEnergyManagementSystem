import { Component, OnInit } from '@angular/core';
import { MatSnackBar } from '@angular/material';
import { HttpService } from '../services/http.service';

@Component({
  selector: 'app-demand',
  templateUrl: './demand.component.html',
  styleUrls: ['./demand.component.scss']
})
export class DemandComponent implements OnInit {

  private currentDate: Date;

  private demandUrl: string = "demandCurrent";

  private demandHistoricalUrl: string = "demandHistorical";

  public chartType: string = 'bar';


  public chartDatasets: Array<any>;

  public chartLabels: Array<any> = [
    'No data gathered.'
  ];

  public chartColors: Array<any> = [{
    backgroundColor:
      'rgba(255, 235, 59, .4)',
    borderColor:
      'rgba(158, 150, 0, 1)',
    borderWidth: 2,
  }];

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
            labelString: 'Power consumed in W'
          }
        }
      ]
    }
  };

  constructor(private snackbar: MatSnackBar, private http: HttpService) {
    let request = this.http.makeGetRequest(this.demandUrl);
    this.requestData(request, true);

  }

  private requestData(request, changeColor: boolean) {

    request.subscribe(
      (data: any) => {
        let chartDatasetsTemp: any = {};
        let chartLabelsTemp: string[] = [];
        let exampleName: string;

        data.map((element, index) => {
          if (index == 0) {
            exampleName = element.building_name;
          }
          // generate labels
          if (exampleName == element.building_name) {
            let timestamp = element.timestamp;
            // cut the string to the hour, set starting cut to 11 if just the hour should be showed
            timestamp = timestamp.slice(0, 13) + "h";
            chartLabelsTemp.push(timestamp);
          }
          chartDatasetsTemp[element.building_name] = chartDatasetsTemp[element.building_name] || []
          chartDatasetsTemp[element.building_name].push(element.demand);

          this.chartLabels = chartLabelsTemp;
          if (changeColor) {
            this.chartColors = [];
            for (let name in chartDatasetsTemp) {
              this.addColor();
            }
          }
          this.chartDatasets = []
          for (let name in chartDatasetsTemp) {
            this.chartDatasets.push({ data: chartDatasetsTemp[name], label: name });
          }
          console.log(this.chartLabels)
        });
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


  historicalData(event) {
    let value = event.value;
    if (!value) {
      return;
    }
    if (this.currentDate == value) {
      return;
    }
    this.currentDate = value;
    let request = this.http.makeGetRequestSpecificDate(this.demandHistoricalUrl, value);
    this.requestData(request, false);

  }

  historicalDataInput(event) {
    this.historicalData(event)

  }

  addColor() {
    this.chartColors.push(
      {
        backgroundColor:
          'rgba(255, 99, 132, 0.2)',
        borderColor:
          'rgba(255, 99, 132, 1)',
        borderWidth: 2,
      }
    );

  }

  ngOnInit() {
  }

  public chartClicked(e: any): void { }
  public chartHovered(e: any): void { }


}