import { Component, OnInit } from '@angular/core';
import { HttpService } from '../services/http.service';
import { MatSnackBar } from '@angular/material';

@Component({
  selector: 'app-settings',
  templateUrl: './settings.component.html',
  styleUrls: ['./settings.component.scss']
})
export class SettingsComponent implements OnInit {
  private url: string = "optimizerObjective"; 
  private optimization: string = "";

  private frontendUrl: string;
  private simulationUrl: string;
  private optimizerUrl: string;
  constructor(private http: HttpService, private snackbar: MatSnackBar) {
    this.frontendUrl = http.baseUrl["Frontend-Service"];
    this.simulationUrl = http.baseUrl["Simulation"];
    this.optimizerUrl = http.baseUrl["Optimizer"];
  }

  changeOptimization(value) {
    let request = this.http.makePostRequestAddOption(this.url, value, {});

    request.subscribe(
      (data: any) => {
        console.log(data)
        
        this.snackbar.open('Objective function changed.', '', {
          duration: 2000
        });
        
      },
      // error handling
      error => {
        console.log(error);
        this.snackbar.open('Could not access optimizer.', '', {
          duration: 3000
        });
      });

  }

  updateUrls() {
    this.http.baseUrl = {
      "Frontend-Service": this.frontendUrl,
      "Simulation": this.simulationUrl,
      "Optimizer": this.optimizerUrl,
    };
  }


  ngOnInit() {
  }

}
