# -*- coding: utf-8 -*-
"""
Author: Mike Ryan
Date: 2024/05/16
License: MIT
"""
from dsg_lib.common_functions.file_functions import open_json, save_json

example_json = {
    "super_cool_people": [
        {
            "name": "Blaise Pascal",
            "famous_for": "Blaise Pascal was a French mathematician, physicist, inventor, writer and Catholic theologian. He was a child prodigy who was educated by his father, a tax collector in Rouen. Pascal's earliest work was in the natural and applied sciences where he made important contributions to the study of fluids, and clarified the concepts of pressure and vacuum by generalising the work of Evangelista Torricelli. Pascal also wrote in defence of the scientific method.",  # noqa: E501
            "birth_date": "Jun 19, 1623",
            "death_date": "Aug 19, 1662",
        },
        {
            "name": "Galileo Galilei",
            "famous_for": 'Galileo di Vincenzo Bonaulti de Galilei was an Italian astronomer, physicist and engineer, sometimes described as a polymath, from Pisa. Galileo has been called the "father of observational astronomy", the "father of modern physics", the "father of the scientific method", and the "father of modern science".',  # noqa: E501
            "birth_date": "Feb 15, 1564",
            "death_date": "Jan 08, 1642",
        },
        {
            "name": "Michelangelo di Lodovico Buonarroti Simoni",
            "famous_for": "Michelangelo di Lodovico Buonarroti Simoni , known best as simply Michelangelo, was an Italian sculptor, painter, architect and poet of the High Renaissance born in the Republic of Florence, who exerted an unparalleled influence on the development of Western art.",  # noqa: E501
            "birth_date": "Mar 06, 1475",
            "death_date": "Feb 18, 1564",
        },
    ],
    "sources": "wikipedia via Google search.",
}


def save_some_data(example_json: str):
    # function requires file_name and data as a string to be sent.
    # see documentation for additonal information
    save_json(file_name="your-file-name.json", data=example_json)


def open_some_data(the_file_name: str) -> dict:
    # function requires file_name and a string will be returned
    # see documentation for additonal information
    result: dict = open_json(file_name=the_file_name)
    return result


if __name__ == "__main__":
    save_some_data(example_json)
    opened_file: dict = open_some_data("your-file-name.json")
    print(opened_file)
