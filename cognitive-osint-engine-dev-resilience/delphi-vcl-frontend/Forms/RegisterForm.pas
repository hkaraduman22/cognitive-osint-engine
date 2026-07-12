unit RegisterForm;

interface

uses
  Winapi.Windows,
  Winapi.Messages,
  System.SysUtils,
  System.Variants,
  System.Classes,
  Vcl.Graphics,
  Vcl.Controls,
  Vcl.Forms,
  Vcl.Dialogs,
  Vcl.StdCtrls;

type
  TFrmRegister = class(TForm)
    LblTitle: TLabel;
    LblUsername: TLabel;
    LblPassword: TLabel;
    LblPasswordAgain: TLabel;
    EdtUsername: TEdit;
    EdtPassword: TEdit;
    EdtPasswordAgain: TEdit;
    BtnRegister: TButton;
    BtnCancel: TButton;
    LblStatus: TLabel;
    procedure BtnRegisterClick(Sender: TObject);
    procedure BtnCancelClick(Sender: TObject);
  private
    procedure SetBusy(const AValue: Boolean);
  public
    { Public declarations }
  end;

var
  FrmRegister: TFrmRegister;

implementation

{$R *.dfm}

uses
  UAuthService,
  UJwtTokenStore;

procedure TFrmRegister.BtnCancelClick(Sender: TObject);
begin
  ModalResult := mrCancel;
end;

procedure TFrmRegister.BtnRegisterClick(Sender: TObject);
var
  LAuthService: TAuthService;
  LToken: string;
  LPassword: string;
  LPasswordAgain: string;
begin
  LPassword := EdtPassword.Text;
  LPasswordAgain := EdtPasswordAgain.Text;
  if LPassword <> LPasswordAgain then
    raise Exception.Create('Sifreler ayni olmali.');

  SetBusy(True);
  try
    LblStatus.Caption := 'Kayit yapiliyor...';

    LAuthService := TAuthService.Create;
    try
      LToken := LAuthService.Register(Trim(EdtUsername.Text), LPassword);
      TJwtTokenStore.SetToken(LToken);
    finally
      LAuthService.Free;
    end;

    LblStatus.Caption := 'Kayit basarili. JWT kaydedildi.';
    ModalResult := mrOk;
  except
    on E: Exception do
      LblStatus.Caption := E.Message;
  end;
  SetBusy(False);
end;

procedure TFrmRegister.SetBusy(const AValue: Boolean);
begin
  BtnRegister.Enabled := not AValue;
  BtnCancel.Enabled := not AValue;
  EdtUsername.Enabled := not AValue;
  EdtPassword.Enabled := not AValue;
  EdtPasswordAgain.Enabled := not AValue;
end;

end.
