import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { AddWindTurbineComponent } from './add-wind-turbine.component';

describe('AddWindTurbineComponent', () => {
  let component: AddWindTurbineComponent;
  let fixture: ComponentFixture<AddWindTurbineComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ AddWindTurbineComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AddWindTurbineComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
