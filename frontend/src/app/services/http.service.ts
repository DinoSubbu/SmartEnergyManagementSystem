import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { HttpParams } from "@angular/common/http";
import { HttpHeaders } from '@angular/common/http';
import { formatDate } from '@angular/common';

const httpOptions = {
  headers: new HttpHeaders({
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*'
  })
};

@Injectable({
  providedIn: 'root'
})
export class HttpService {
  public url: any = {
    "addBattery": "battery/create",
    "addBuilding": "building/create",
    "addSolar": "solarpanel/create",
    "addWindTurbine": "windturbine/create",
    "batteryForecast": "optimizer/getSchedule/",
    "components": "optimizer/getSchedule/",
    "schedule": "optimizer/getSchedule/",
    "day-ahead-prices": "price/getlatest",
    "co2Forecast": "co2/getlatest",
    "gasBoilerLatest": "gasBoiler/getlatest/",
    "windForecast": "forecast/wind/getAll/",
    "solarForecast": "forecast/solar/getAll/",
    "optimizerObjective": "optimizer/setObjective/",
    "simulationInit": "simulation/start",
    "simulationStarted": "simulation/isStarted",
    "simulationInitUndo": "simulation/undo",
    "batteryLatest": "battery/current_sim_latest",
    "windLatest": "windturbine/current_sim_latest",
    "solarLatest": "solarpanel/current_sim_latest",
    "demandLatest": "building/current_sim_latest",
    "batteryCurrent": "battery/current_sim_latest",
    "windCurrent": "windturbine/current_sim",
    "solarCurrent": "solarpanel/current_sim",
    "demandCurrent": "building/current_sim",
    "simulationDemand": "total/sim/",
    "windHistorical": "windturbine/sim/",
    "solarHistorical": "solarpanel/sim/",
    "demandHistorical": "building/sim/",
    "getBuildings": "building/getAll",
    "getBatteries": "battery/getAll",
    "getSolar": "solarpanel/getAll",
    "getWind": "windturbine/getAll",
  }

  public baseUrl: any = {
    "Frontend-Service": "http://localhost:5000/",
    "Simulation": "http://localhost:5002/",
    "Optimizer": "http://localhost:5004/",
  }

  constructor(private httpClient: HttpClient) { }


  /**
   * appends the datetime of the next day to the url to get just the forecast results
   */
  private forgeNextDateUrl(url: string) {
    // converts to given datetime format    
    var datetime = new Date();
    var tomorrow = new Date();
    // sets the date to the date of the next day and the time to 0 to get the whole information from the next day
    tomorrow.setDate(datetime.getDate() + 1);
    tomorrow.setHours(0)
    tomorrow.setMinutes(0)
    tomorrow.setSeconds(0)
    return this.forgeDateUrl(url, tomorrow);
  }

  private forgeDateUrl(url: string, date: Date) {
    let urlFinal = url + formatDate(date, 'yyyy-MM-ddTHH:mm:ss', 'de-DE');
    return urlFinal;
  }

  /**
   * appends the datetime of the current day to the url to get just the forecast results
   */
  private forgeCurrentDateUrl(url: string) {
    // converts to given datetime format    
    var datetime = new Date();
    var tomorrow = new Date();
    // sets the date to the date of the next day and the time to 0 to get the whole information from the next day
    tomorrow.setDate(datetime.getDate());
    tomorrow.setHours(0)
    tomorrow.setMinutes(0)
    tomorrow.setSeconds(0)
    return this.forgeDateUrl(url, tomorrow);
  }

  private forgeUrl(key: string) {
    let baseUrlTemp = ""
    if (key == "optimizerObjective") {
      baseUrlTemp = this.baseUrl["Optimizer"];
    } else if (key =="simulationInitUndo") {
      baseUrlTemp = this.baseUrl["Simulation"];
    } else {
      baseUrlTemp = this.baseUrl["Frontend-Service"];
    }
    return baseUrlTemp + this.url[key];
  }

  makeGetRequest(key: string) {
    return this.httpClient.get(this.forgeUrl(key));
  }

  makeGetRequestAddTime(key: string) {
    let urlFinal = this.forgeNextDateUrl(this.forgeUrl(key));
    return this.httpClient.get(urlFinal);
  }

  makeGetRequestAddCurrentTime(key: string) {
    let urlFinal = this.forgeCurrentDateUrl(this.forgeUrl(key));
    return this.httpClient.get(urlFinal);
  }

  makeGetRequestAddOption(key: string, option: string) {
    let urlFinal = this.forgeUrl(key) + option;
    return this.httpClient.get(urlFinal);
  }

  makeGetRequestSpecificDate(key: string, date: Date) {
    let urlFinal = this.forgeDateUrl(this.forgeUrl(key), date);
    return this.httpClient.get(urlFinal);
  }

  makePostRequest(key: string, requestBody: any) {
    return this.httpClient.post(this.forgeUrl(key), requestBody, httpOptions);
  }

  makePostRequestAddOption(key: string, option: string, requestBody: any) {
    let urlFinal = this.forgeUrl(key) + option;
    return this.httpClient.post(urlFinal, requestBody, httpOptions);
  }
}
