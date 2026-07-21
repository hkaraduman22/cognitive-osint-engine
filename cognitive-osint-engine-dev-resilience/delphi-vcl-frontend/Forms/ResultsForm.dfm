object FrmResults: TFrmResults
  Left = 0
  Top = 0
  BorderStyle = bsSingle
  Caption = 'Sonuclar'
  ClientHeight = 610
  ClientWidth = 860
  Color = clWhite
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -13
  Font.Name = 'Segoe UI'
  Font.Style = []
  Position = poMainFormCenter
  TextHeight = 17
  object LblTitle: TLabel
    Left = 24
    Top = 18
    Width = 104
    Height = 33
    Caption = 'Sonuclar'
    Font.Charset = DEFAULT_CHARSET
    Font.Color = $00A0522D
    Font.Height = -24
    Font.Name = 'Segoe UI'
    Font.Style = [fsBold]
    ParentFont = False
  end
  object LblAramaId: TLabel
    Left = 24
    Top = 72
    Width = 62
    Height = 17
    Caption = 'Arama ID'
    Font.Color = $00808080
  end
  object LblStatus: TLabel
    Left = 24
    Top = 568
    Width = 46
    Height = 17
    Caption = 'Durum:'
    Font.Color = $00606060
  end
  object EdtAramaId: TEdit
    Left = 24
    Top = 94
    Width = 200
    Height = 27
    BorderStyle = bsSingle
    Color = clWhite
    Font.Height = -12
    TabOrder = 0
  end
  object BtnLoad: TButton
    Left = 236
    Top = 90
    Width = 120
    Height = 34
    Caption = 'Getir'
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -12
    Font.Name = 'Segoe UI'
    Font.Style = [fsBold]
    ParentFont = False
    TabOrder = 1
    OnClick = BtnLoadClick
  end
  object BtnClose: TButton
    Left = 368
    Top = 90
    Width = 120
    Height = 34
    Caption = 'Kapat'
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWindowText
    Font.Height = -12
    Font.Name = 'Segoe UI'
    Font.Style = []
    TabOrder = 2
    OnClick = BtnCloseClick
  end
  object MemoResults: TMemo
    Left = 24
    Top = 138
    Width = 812
    Height = 418
    BorderStyle = bsSingle
    Color = $00F9F9FA
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWindowText
    Font.Height = -12
    Font.Name = 'Consolas'
    Font.Style = []
    ScrollBars = ssVertical
    TabOrder = 3
  end
end
