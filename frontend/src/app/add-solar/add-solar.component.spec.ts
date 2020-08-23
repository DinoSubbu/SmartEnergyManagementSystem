import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { AddSolarComponent } from './add-solar.component';

describe('AddSolarComponent', () => {
  let component: AddSolarComponent;
  let fixture: ComponentFixture<AddSolarComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ AddSolarComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AddSolarComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
