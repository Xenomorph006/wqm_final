import torch

from .lnn import LiquidNeuralNetwork


def main():

    batch_size = 8

    sequence_length = 60

    features = 5

    prediction_horizon = 12

    model = LiquidNeuralNetwork(
        input_size=features,
        hidden_size=64,
        output_size=features,
        prediction_horizon=prediction_horizon,
    )

    x = torch.randn(
        batch_size,
        sequence_length,
        features,
    )

    predictions, confidence = model(x)

    print("Input:")
    print(x.shape)

    print()

    print("Predictions:")
    print(predictions.shape)

    print()

    print("Confidence:")
    print(confidence.shape)

    print()

    print(
        "Prediction range:",
        predictions.min().item(),
        predictions.max().item(),
    )

    print(
        "Confidence range:",
        confidence.min().item(),
        confidence.max().item(),
    )


if __name__ == "__main__":
    main()