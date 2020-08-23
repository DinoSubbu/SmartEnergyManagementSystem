import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { DayAheadPricesComponent } from './day-ahead-prices.component';

describe('DayAheadPricesComponent', () => {
  let component: DayAheadPricesComponent;
  let fixture: ComponentFixture<DayAheadPricesComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ DayAheadPricesComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(DayAheadPricesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
