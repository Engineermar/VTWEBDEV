package edu.gatech.seclass.sdpsalarycomp;

import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.TextView;

import java.util.ArrayList;
import java.util.List;

import edu.gatech.seclass.sdpsalarycomp.R;

public class SDPSalaryCompActivity extends AppCompatActivity {

    private EditText inputSalary;
    private Spinner currentCity;
    private Spinner newCity;
    private TextView outputSalary;
    private int[] salaries = {160, 152, 197, 201, 153, 244, 232, 241, 198, 114, 139, 217};

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_sdpsalary_comp);
        initializeViews();
        inputSalary.addTextChangedListener(new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {
                //Do Nothing
            }

            @Override
            public void onTextChanged(CharSequence s, int start, int before, int count) {
                //setValue(s.toString());
            }

            @Override
            public void afterTextChanged(Editable s) {
                setValue(s.toString());
                if (s.toString().contains("-")) {
                    inputSalary.setError(getResources().getString(R.string.error_salary));
                }
            }
        });
    }

    private void setValue(String s) {
        if (s != null && isInteger(s)) {
            if (currentCity.getSelectedItem().toString() != null && newCity.getSelectedItem().toString() != null) {
                calculations(s.equals("")? "0":s, currentCity.getSelectedItemPosition(), newCity.getSelectedItemPosition());
            } else {
                outputSalary.setText("");
            }
        } else {
            outputSalary.setText("");
            inputSalary.setError(getResources().getString(R.string.error_salary));
        }
    }

    private boolean isInteger(String s) {
        try
        {
            Integer.parseInt(s);
            return true;
        } catch (NumberFormatException ex)
        {
            return false;
        }
    }

    private void calculations(String s, int cuurentCityNum, int newCityNum) {
        int input = Integer.parseInt(s);
        double stepOne = input * salaries[newCityNum];
        int stepTwo = (int) Math.round(stepOne / salaries[cuurentCityNum]);
        outputSalary.setText(stepTwo+"");
    }

    private void initializeViews() {
        inputSalary = findViewById(R.id.baseSalary);
        currentCity = findViewById(R.id.currentCity);
        newCity = findViewById(R.id.newCity);
        outputSalary = findViewById(R.id.targetSalary);

        // Spinner Drop down elements
        List<String> cities = new ArrayList<String>();
        cities.add("Atlanta, GA");
        cities.add("Austin, TX");
        cities.add("Boston, MA");
        cities.add("Honolulu, HI");
        cities.add("Las Vegas, NV");
        cities.add("Mountain View, CA");
        cities.add("New York City, NY");
        cities.add("San Francisco, CA");
        cities.add("Seattle, WA");
        cities.add("Springfield, MO");
        cities.add("Tampa, FL");
        cities.add("Washington D.C.");

        ArrayAdapter<String> adapter = new ArrayAdapter<String>(this, android.R.layout.simple_spinner_item, cities);
        currentCity.setAdapter(adapter);
        newCity.setAdapter(adapter);

        AdapterView.OnItemSelectedListener itemClickListener = new AdapterView.OnItemSelectedListener() {
            @Override
            public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
                setValue(inputSalary.getText().toString());
            }

            @Override
            public void onNothingSelected(AdapterView<?> parent) {

            }
        };

        currentCity.setOnItemSelectedListener(itemClickListener);
        newCity.setOnItemSelectedListener(itemClickListener);
    }
}
